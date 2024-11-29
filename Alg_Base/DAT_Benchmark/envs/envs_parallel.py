import asyncio
import numpy as np
from torch.utils.tensorboard import SummaryWriter
import concurrent.futures
import time
import os


def GE(num, env_conf: dict):  # Benchmark
    from envs.environment import BenchEnv_Multi, process_frame
    from functools import partial

    res = []
    for _ in range(num):
        res.append(
            BenchEnv_Multi(
                Action_dim=env_conf["Action_dim"],
                process_state=partial(process_frame, conf=env_conf),
                arg_worker=num,
                process_idx=_,
                Other_State=env_conf["Other_State"],
                CloudPoint=env_conf["CloudPoint"],
                RewardParams=env_conf["RewardParams"],
                action_list=[
                    env_conf["Forward_Speed"],
                    env_conf["Backward_Speed"],
                    env_conf["Left_Speed"],
                    env_conf["Right_Speed"],
                    env_conf["CW_omega"],
                    env_conf["CCW_omega"],
                ],
                port_process=env_conf["port_process"],
                end_reward=env_conf["end_reward"],
                end_reward_list=env_conf["end_reward_list"],
                scene=env_conf["scene"],
                weather=env_conf["weather"],
                auto_start=env_conf["auto_start"],
                Control_Frequence=env_conf["Control_Frequence"],
                reward_type=env_conf["RewardType"],
                verbose=env_conf["verbose"],
                delay=env_conf["delay"],
            )
        )
    return res


def train_log_reset():
    try:
        os.remove("./models/R_VAT/RVAT_logs/steps.txt")
        print("Log initialize success")
    except FileNotFoundError:
        print("No Need for log init")
    except Exception as e:
        print(f"Log init failed: {e}")


class Envs:
    class Env:
        def __init__(self, env):
            self.env = env
            self.state = None
            self.reward = None
            self.done = None
            self.should_reset = False

        def reset(self):
            self.state, _ = self.env.reset()

        def step(self, action: int):
            if self.should_reset:
                self.state, _ = self.env.reset()
                self.should_reset = False
            else:
                self.state, self.reward, self.done, _ = self.env.step(action)
                if self.done > 0.5:
                    self.should_reset = True

    class Env_T: 
        def __init__(self, env):
            self.env = env
            self.state = None
            self.reward = None
            self.done = None
            self.should_reset = False

            self.rewards = 0

        def reset(self):
            self.state, _ = self.env.reset()

        def step(self, action: int):
            if self.should_reset:
                self.state, _ = self.env.reset()
                self.should_reset = False
                self.rewards = 0
            else:
                self.state, self.reward, self.done, _ = self.env.step(action)
                if self.done > 0.5:
                    self.should_reset = True

                self.rewards += self.reward

    def __init__(self, *args, **kwargs):

        self.num_envs = kwargs["num_envs"]
        assert self.num_envs > 0

        if "env_list" in kwargs:
            self.env_list = [self.Env(env) for env in kwargs["env_list"]]
        else:
            self.env_list = []
            for _ in range(self.num_envs):
                self.env_list.append(
                    self.Env(kwargs["env_mk"](*(kwargs["env_mk_args"])))
                )

        self.states = None
        self.rewards = None
        self.done = None

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.num_envs)

        if "logs_show" in kwargs:
            self.logs = kwargs["logs_show"]
            if self.logs > 0:
                self.SummaryWriter = SummaryWriter("./models/R_VAT/RVAT_logs")

                for i in range(self.logs):
                    _env = self.env_list[i].env
                    self.env_list[i] = self.Env_T(_env)

                self.steps = 0

                self.st = time.time()
                self.ts = 0

                if os.path.exists("./models/R_VAT/RVAT_logs/steps.txt"):
                    with open("./models/R_VAT/RVAT_logs/steps.txt", "r") as file:
                        self.steps = int(file.readline().strip())
                else:
                    self.SummaryWriter.add_scalar("rewards", 0, 0)

    async def reset_(self):
        loop = asyncio.get_running_loop()
        await asyncio.gather(
            *tuple(
                [
                    loop.run_in_executor(self.executor, env.reset)
                    for env in self.env_list
                ]
            )
        )
        self.states = np.array([env.state for env in self.env_list])

    async def step_(self, actions):
        loop = asyncio.get_running_loop()
        await asyncio.gather(
            *tuple(
                [
                    loop.run_in_executor(
                        self.executor, self.env_list[i].step, actions[i]
                    )
                    for i in range(self.num_envs)
                ]
            )
        )
        self.states, self.rewards, self.done = (
            np.array([env.state for env in self.env_list]),
            np.array([env.reward for env in self.env_list]),
            np.array([env.done for env in self.env_list]),
        )

    def reset(self):
        asyncio.run(self.reset_())
        return self.states

    def step(self, actions):
        asyncio.run(self.step_(actions))

        if self.logs > 0:
            self.steps += 1
            self.ts += 1
            rs = 0
            tot = 0
            for i in range(self.logs):
                if self.env_list[i].should_reset and self.env_list[i].rewards > 0:
                    rs += self.env_list[i].rewards
                    tot += 1
            if tot > 0:
                self.SummaryWriter.add_scalar("rewards", rs / tot, self.steps)
            self.SummaryWriter.add_scalar(
                "runtime/step (s)", (time.time() - self.st) / self.ts, self.ts
            )
            with open("./models/R_VAT/RVAT_logs/steps.txt", "w") as file:
                file.write(str(self.steps))

        return self.states, self.rewards, self.done
