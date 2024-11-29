import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import gymnasium
from tianshou.data import Batch
from tianshou.data.types import ObsBatchProtocol
from tianshou.policy import DiscreteSACPolicy
from tianshou.utils.net.common import Net
from tianshou.utils.net.continuous import ActorProb
from torch.optim import Adam
from customCNN import CustomCNN

class DenseMlp(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=256, squash_output=True):
        super(DenseMlp, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.squash_output = squash_output
        self.layer_1 = nn.Linear(input_dim, hidden_dim)
        self.layer_2 = nn.Linear(hidden_dim, hidden_dim)
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        self.output_activation = nn.Softmax(dim=-1) if squash_output else nn.Identity()

        # get device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def forward(self, x:np.ndarray):
        if isinstance(x,np.ndarray):
            x = torch.tensor(x).to(self.device)
        out_1 = F.relu(self.layer_1(x))
        out_2 = F.relu(self.layer_2(out_1))
        x = self.output_layer(out_2)
        return self.output_activation(x)

class CustomDiscreteActor(nn.Module):

    def __init__(self, observation_space:gymnasium.spaces.Box, action_dim:int, hidden_sizes=(512,)):
        super().__init__()
        self.feature_extractor = CustomCNN(observation_space)
        feature_dim = self.feature_extractor.linear[-2].out_features
        self.net = DenseMlp(feature_dim, action_dim, hidden_dim=hidden_sizes[0])

    def forward(self, obs, state=None, info={}):
        features = self.feature_extractor(obs)
        logits = self.net(features)
        return logits, state

class CustomDiscreteCritic(nn.Module):

    def __init__(self, obs_shape_critic, action_shape, hidden_sizes=(256,)):
        super().__init__()
        self.net = DenseMlp(obs_shape_critic, action_shape, hidden_dim=hidden_sizes[0])

    def forward(self, obs):
        q_values = self.net(obs)
        return q_values

from typing import Any, TypeVar, cast
import numpy as np
import torch
from torch.distributions import Categorical
import time 

from tianshou.policy.modelfree.discrete_sac import TDiscreteSACTrainingStats,DiscreteSACTrainingStats
from tianshou.data import Batch, ReplayBuffer, to_torch
from tianshou.data.types import ObsBatchProtocol, RolloutBatchProtocol
from tianshou.policy.base import TLearningRateScheduler
from tianshou.policy.modelfree.sac import SACTrainingStats
from tianshou.utils.net.discrete import Actor, Critic


class DVAT_SACDPolicy(DiscreteSACPolicy):
    """Implementation of SAC for Discrete Action Settings. arXiv:1910.07207.

    :param actor: the actor network following the rules (s_B -> dist_input_BD)
    :param actor_optim: the optimizer for actor network.
    :param critic: the first critic network. (s, a -> Q(s, a))
    :param critic_optim: the optimizer for the first critic network.
    :param action_space: Env's action space. Should be gym.spaces.Box.
    :param critic2: the second critic network. (s, a -> Q(s, a)).
        If None, use the same network as critic (via deepcopy).
    :param critic2_optim: the optimizer for the second critic network.
        If None, clone critic_optim to use for critic2.parameters().
    :param tau: param for soft update of the target network.
    :param gamma: discount factor, in [0, 1].
    :param alpha: entropy regularization coefficient.
        If a tuple (target_entropy, log_alpha, alpha_optim) is provided,
        then alpha is automatically tuned.
    :param estimation_step: the number of steps to look ahead for calculating
    :param observation_space: Env's observation space.
    :param lr_scheduler: a learning rate scheduler that adjusts the learning rate
        in optimizer in each policy.update()

    .. seealso::

        Please refer to :class:`~tianshou.policy.BasePolicy` for more detailed
        explanation.
    """

    def __init__(
        self,
        *,
        actor: torch.nn.Module | Actor,
        actor_optim: torch.optim.Optimizer,
        critic: torch.nn.Module | Critic,
        critic_optim: torch.optim.Optimizer,
        action_space: gymnasium.spaces.Discrete,
        critic2: torch.nn.Module | Critic | None = None,
        critic2_optim: torch.optim.Optimizer | None = None,
        tau: float = 0.005,
        gamma: float = 0.99,
        alpha: float | tuple[float, torch.Tensor, torch.optim.Optimizer] = 0.2,
        estimation_step: int = 1,
        observation_space: gymnasium.Space | None = None,
        lr_scheduler: TLearningRateScheduler | None = None,
    ) -> None:
        self.start_time = time.time()
        super().__init__(
            actor=actor,
            actor_optim=actor_optim,
            critic=critic,
            critic_optim=critic_optim,
            action_space=action_space,
            critic2=critic2,
            critic2_optim=critic2_optim,
            tau=tau,
            gamma=gamma,
            alpha=alpha,
            estimation_step=estimation_step,
            observation_space=observation_space,
            lr_scheduler=lr_scheduler,
        )

    def forward(  # type: ignore
        self,
        batch: ObsBatchProtocol,
        state: dict | Batch | np.ndarray | None = None,
        **kwargs: Any,
    ) -> Batch:
        logits_BA, hidden_BH = self.actor(batch.obs["actor_obs"], state=state, info=batch.info)
        dist = Categorical(logits=logits_BA)
        act_B = (
            dist.mode
            if self.deterministic_eval and not self.is_within_training_step
            else dist.sample()
        )
        return Batch(logits=logits_BA, act=act_B, state=hidden_BH, dist=dist)

    def _target_q(self, buffer: ReplayBuffer, indices: np.ndarray) -> torch.Tensor:
        obs_next_batch = Batch(
            obs=buffer[indices].obs_next,
            info=[None] * len(indices),
        )  # obs_next: s_{t+n}
        obs_next_result = self(obs_next_batch)
        dist = obs_next_result.dist
        target_q = dist.probs * torch.min(
            self.critic_old(obs_next_batch.obs["critic_obs"]),
            self.critic2_old(obs_next_batch.obs["critic_obs"]),
        )
        return target_q.sum(dim=-1) + self.alpha * dist.entropy()

    def learn(self, batch: RolloutBatchProtocol,target_q:torch.Tensor,*args: Any, **kwargs: Any) -> TDiscreteSACTrainingStats:  # type: ignore
        weight = batch.pop("weight", 1.0)
        act = to_torch(batch.act[:, np.newaxis], device=target_q.device, dtype=torch.long)

        # critic 1
        current_q1 = self.critic(batch.obs["critic_obs"]).gather(1, act).flatten()
        td1 = current_q1 - target_q
        critic1_loss = (td1.pow(2) * weight).mean()

        self.critic_optim.zero_grad()
        critic1_loss.backward(retain_graph=True)
        self.critic_optim.step()

        # critic 2
        current_q2 = self.critic2(batch.obs["critic_obs"]).gather(1, act).flatten()
        td2 = current_q2 - target_q
        critic2_loss = (td2.pow(2) * weight).mean()

        self.critic2_optim.zero_grad()
        critic2_loss.backward()
        self.critic2_optim.step()
        batch.weight = (td1 + td2) / 2.0  # prio-buffer

        # actor
        dist = self(batch).dist
        entropy = dist.entropy()
        with torch.no_grad():
            current_q1a = self.critic(batch.obs["critic_obs"])
            current_q2a = self.critic2(batch.obs["critic_obs"])
            q = torch.min(current_q1a, current_q2a)
        actor_loss = -(self.alpha * entropy + (dist.probs * q).sum(dim=-1)).mean()
        self.actor_optim.zero_grad()
        actor_loss.backward()
        self.actor_optim.step()

        if self.is_auto_alpha:
            log_prob = -entropy.detach() + self.target_entropy
            alpha_loss = -(self.log_alpha * log_prob).mean()
            self.alpha_optim.zero_grad()
            alpha_loss.backward()
            self.alpha_optim.step()
            self.alpha = self.log_alpha.detach().exp()

        self.sync_weight()

        if self.is_auto_alpha:
            self.alpha = cast(torch.Tensor, self.alpha)

        train_time = time.time()-self.start_time

        return DiscreteSACTrainingStats(  # type: ignore[return-value]
            train_time=train_time,
            actor_loss=actor_loss.item(),
            critic1_loss=critic1_loss.item(),
            critic2_loss=critic2_loss.item(),
            alpha=self.alpha.item() if isinstance(self.alpha, torch.Tensor) else self.alpha,
            alpha_loss=None if not self.is_auto_alpha else alpha_loss.item(),
        )
    

def create_sacd_policy(actor_obs_space:gymnasium.spaces.Box,action_space:gymnasium.spaces.Box,obs_shape_critic:int, action_shape:int, lr=3e-4, gamma=0.99, tau=0.005, alpha=0.2)->DVAT_SACDPolicy:
    # check variable type
    assert isinstance(actor_obs_space,gymnasium.spaces.Box)
    assert isinstance(obs_shape_critic,int)
    assert isinstance(action_shape,int)

    # get device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # actor,critic1,critic2
    actor = CustomDiscreteActor(actor_obs_space, action_shape).to(device)
    critic1 = CustomDiscreteCritic(obs_shape_critic, action_shape).to(device)
    critic2 = CustomDiscreteCritic(obs_shape_critic, action_shape).to(device)

    # optimizer
    actor_optim = Adam(actor.parameters(), lr=lr)
    critic1_optim = Adam(critic1.parameters(), lr=lr)
    critic2_optim = Adam(critic2.parameters(), lr=lr)

    # Discrete SAC Policy
    sacd_policy = DVAT_SACDPolicy(
        actor=actor,
        actor_optim=actor_optim,
        critic=critic1,
        critic_optim=critic1_optim,
        action_space=action_space,
        critic2=critic2,
        critic2_optim=critic2_optim,
        tau=tau,
        gamma=gamma,
        alpha=alpha
    )

    return sacd_policy


## Get action from single state
def get_action(sacd_policy:DVAT_SACDPolicy, state):
    # turn state into Batch
    state_batch = Batch(obs=state)
    
    # add info to Batch object
    if "info" not in state_batch:
        state_batch.info = {}
    # get action by sacd_policy.forward
    sacd_policy.deterministic_eval = True # use deterministic action instead of sample
    result = sacd_policy.forward(state_batch)
    
    # return action
    return result.act
