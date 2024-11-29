import multiprocessing
from multiprocessing import connection
from multiprocessing.context import BaseContext
from typing import Literal
from tianshou.env.worker.subproc import ShArray,SubprocEnvWorker,_setup_buf
from tianshou.env.venvs import BaseVectorEnv
from tianshou.env.utils import ENV_TYPE
from tianshou.env.utils import CloudpickleWrapper
from tianshou.env.worker import EnvWorker
import numpy as np
from collections.abc import Sequence
from typing import Callable
import gymnasium

def _worker_tianshou(
    parent: connection.Connection,
    p: connection.Connection,
    env_fn_wrapper: CloudpickleWrapper,
    obs_bufs: dict | tuple | ShArray | None = None,
) -> None:
    def _encode_obs(
        obs: dict | tuple | np.ndarray,
        buffer: dict | tuple | ShArray,
    ) -> None:
        if isinstance(obs, np.ndarray) and isinstance(buffer, ShArray):
            buffer.save(obs)
        elif isinstance(obs, tuple) and isinstance(buffer, tuple):
            for o, b in zip(obs, buffer, strict=True):
                _encode_obs(o, b)
        elif isinstance(obs, dict) and isinstance(buffer, dict):
            for k in obs:
                _encode_obs(obs[k], buffer[k])

    parent.close()
    env = env_fn_wrapper.data()
    try:
        while True:
            try:
                cmd, data = p.recv()
            except EOFError:  # the pipe has been closed
                p.close()
                break
            try:
                done
            except:
                done = False
            if cmd == "step":
                if not done:
                    env_return = env.step(data)
                    done = env_return[2] or env_return[3]
                    if obs_bufs is not None:
                        _encode_obs(env_return[0], obs_bufs)
                        env_return = (None, *env_return[1:])
                    p.send(env_return)
                else:
                    done = False
                    obs, info = env.reset()
                    if obs_bufs is not None:
                        _encode_obs(obs, obs_bufs)
                        obs = None
                    p.send((obs,0.0,0.0,False,info))
            elif cmd == "reset":
                obs, info = env.reset(**data)
                if obs_bufs is not None:
                    _encode_obs(obs, obs_bufs)
                    obs = None
                p.send((obs, info))
            elif cmd == "close":
                p.send(env.close())
                p.close()
                break
            elif cmd == "render":
                p.send(env.render(**data) if hasattr(env, "render") else None)
            elif cmd == "seed":
                if hasattr(env, "seed"):
                    p.send(env.seed(data))
                else:
                    env.action_space.seed(seed=data)
                    env.reset(seed=data)
                    p.send(None)
            elif cmd == "getattr":
                p.send(getattr(env, data) if hasattr(env, data) else None)
            elif cmd == "setattr":
                setattr(env.unwrapped, data["key"], data["value"])
            else:
                p.close()
                raise NotImplementedError
    except KeyboardInterrupt:
        p.close()

class SubprocEnvWorker_TS(SubprocEnvWorker,EnvWorker):
    """Subprocess worker used in SubprocVectorEnv and ShmemVectorEnv."""

    def __init__(
        self,
        env_fn: Callable[[], gymnasium.Env],
        share_memory: bool = False,
        context: BaseContext | Literal["fork", "spawn"] | None = None,
    ) -> None:
        if not isinstance(context, BaseContext):
            context = multiprocessing.get_context(context)
        self.parent_remote, self.child_remote = context.Pipe()
        self.share_memory = share_memory
        self.buffer: dict | tuple | ShArray | None = None
        assert hasattr(context, "Process")  # for mypy
        if self.share_memory:
            dummy = env_fn()
            obs_space = dummy.observation_space
            dummy.close()
            del dummy
            self.buffer = _setup_buf(obs_space, context)
        args = (
            self.parent_remote,
            self.child_remote,
            CloudpickleWrapper(env_fn),
            self.buffer,
        )
        self.process = context.Process(target=_worker_tianshou, args=args, daemon=True)
        self.process.start()
        self.child_remote.close()
        EnvWorker.__init__(self,env_fn)


class SubprocVectorEnv_TS(BaseVectorEnv):
    def __init__(
        self,
        env_fns: Sequence[Callable[[], ENV_TYPE]],
        wait_num: int | None = None,
        timeout: float | None = None,
        share_memory: bool = False,
        context: Literal["fork", "spawn"] | None = None,
    ) -> None:
        def worker_fn(fn: Callable[[], gymnasium.Env]) -> SubprocEnvWorker:
            return SubprocEnvWorker_TS(fn, share_memory=share_memory, context=context)

        super().__init__(
            env_fns,
            worker_fn,
            wait_num,
            timeout,
        )

from tianshou.data import Collector,ReplayBuffer,CollectStats,AsyncCollector,Batch
from tianshou.data.types import RolloutBatchProtocol
from tianshou.data.collector import _nullable_slice
from tianshou.policy import BasePolicy
from typing import Any,cast
from copy import copy
import gymnasium
import time

class TS_Collector(Collector):
    def __init__(self,
        policy: BasePolicy,
        env: gymnasium.Env | BaseVectorEnv,
        buffer: ReplayBuffer | None = None,
        exploration_noise: bool = False,
    ) -> None:
        super().__init__(policy, env, buffer, exploration_noise=exploration_noise)

    def _collect(
        self,
        n_step: int | None = None,
        n_episode: int | None = None,
        random: bool = False,
        render: float | None = None,
        gym_reset_kwargs: dict[str, Any] | None = None,
    ) -> CollectStats:
        # TODO: can't do it init since AsyncCollector is currently a subclass of Collector
        if self.env.is_async:
            raise ValueError(
                f"Please use {AsyncCollector.__name__} for asynchronous environments. "
                f"Env class: {self.env.__class__.__name__}.",
            )

        if n_step is not None:
            ready_env_ids_R = np.arange(self.env_num)
        elif n_episode is not None:
            ready_env_ids_R = np.arange(min(self.env_num, n_episode))
        else:
            raise ValueError("Either n_step or n_episode should be set.")

        start_time = time.time()
        if self._pre_collect_obs_RO is None or self._pre_collect_info_R is None:
            raise ValueError(
                "Initial obs and info should not be None. "
                "Either reset the collector (using reset or reset_env) or pass reset_before_collect=True to collect.",
            )

        step_count = 0
        num_collected_episodes = 0
        episode_returns: list[float] = []
        episode_lens: list[int] = []
        episode_start_indices: list[int] = []

        # in case we select fewer episodes than envs, we run only some of them
        last_obs_RO = _nullable_slice(self._pre_collect_obs_RO, ready_env_ids_R)
        last_info_R = _nullable_slice(self._pre_collect_info_R, ready_env_ids_R)
        last_hidden_state_RH = _nullable_slice(
            self._pre_collect_hidden_state_RH,
            ready_env_ids_R,
        )

        while True:

            # get the next action
            (
                act_RA,
                act_normalized_RA,
                policy_R,
                hidden_state_RH,
            ) = self._compute_action_policy_hidden(
                random=random,
                ready_env_ids_R=ready_env_ids_R,
                last_obs_RO=last_obs_RO,
                last_info_R=last_info_R,
                last_hidden_state_RH=last_hidden_state_RH,
            )
            
            ## Core Function:Step 
            obs_next_RO, rew_R, terminated_R, truncated_R, info_R = self.env.step(
                act_normalized_RA,
                ready_env_ids_R,
            )
            if isinstance(info_R, dict):  # type: ignore[unreachable]
                # This can happen if the env is an envpool env. Then the info returned by step is a dict
                info_R = _dict_of_arr_to_arr_of_dicts(info_R)  # type: ignore[unreachable]
            done_R = np.logical_or(terminated_R, truncated_R)

            current_iteration_batch = cast(
                RolloutBatchProtocol,
                Batch(
                    obs=last_obs_RO,
                    act=act_RA,
                    policy=policy_R,
                    obs_next=obs_next_RO,
                    rew=rew_R,
                    terminated=terminated_R,
                    truncated=truncated_R,
                    done=done_R,
                    info=info_R,
                ),
            )

            if render:
                self.env.render()
                if not np.isclose(render, 0):
                    time.sleep(render)

            # add data into the buffer
            ptr_R, ep_rew_R, ep_len_R, ep_idx_R = self.buffer.add(
                current_iteration_batch,
                buffer_ids=ready_env_ids_R,
            )

            # collect statistics
            num_episodes_done_this_iter = np.sum(done_R)
            num_collected_episodes += num_episodes_done_this_iter
            step_count += len(ready_env_ids_R)

            last_obs_RO = copy(obs_next_RO)
            last_info_R = copy(info_R)
            last_hidden_state_RH = copy(hidden_state_RH)

            if (n_step and step_count >= n_step) or (
                n_episode and num_collected_episodes >= n_episode
            ):
                break

        # generate statistics
        self.collect_step += step_count
        self.collect_episode += num_collected_episodes
        collect_time = max(time.time() - start_time, 1e-9)
        self.collect_time += collect_time

        if n_step:
            # persist for future collect iterations
            self._pre_collect_obs_RO = last_obs_RO
            self._pre_collect_info_R = last_info_R
            self._pre_collect_hidden_state_RH = last_hidden_state_RH
        elif n_episode:
            # reset envs and the _pre_collect fields
            self.reset_env(gym_reset_kwargs)  # todo still necessary?

        return CollectStats.with_autogenerated_stats(
            returns=np.array(episode_returns),
            lens=np.array(episode_lens),
            n_collected_episodes=num_collected_episodes,
            n_collected_steps=step_count,
            collect_time=collect_time,
            collect_speed=step_count / collect_time,
        )
        