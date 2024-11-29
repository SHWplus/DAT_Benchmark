import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

import gymnasium
from torch.utils.tensorboard import SummaryWriter
from copy import deepcopy
import numpy as np

from utils import read_config
from envs.environment import general_env
from envs.gym_envs import CONF,ENV_CONF

class DVAT_ENV(gymnasium.Env):
    def __init__(self,arg_worker:int=1,conf_path:str=CONF,env_conf_path:str=ENV_CONF,process_idx:int=0,end_reward:bool = False,log_dir:str=None,obs_buffer_len:int=3,use_tb:bool=True,train:bool=True) -> None:
        super(DVAT_ENV,self).__init__()

        ## Read Json files
        conf_json = read_config(conf_path)
        env_conf = conf_json["Benchmark"] # env_conf:dict
        
        ## Config Action space
        self.action_space = gymnasium.spaces.Discrete(int(env_conf["Action_dim"]))
        
        ## Config observation space
        image_shape = (env_conf["State_channel"], env_conf["State_size"], env_conf["State_size"])
        assert obs_buffer_len >= 0 and isinstance(obs_buffer_len,int)
        
        self.observation_space = gymnasium.spaces.Dict({
            "actor_obs":gymnasium.spaces.Box(low=0,high=1.0,shape=(obs_buffer_len,)+image_shape,dtype=np.float32),
            "critic_obs":gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(9,), dtype=np.float32),
        })
        ## Init actor_obs and critic_obs
        self.actor_obs = np.zeros((obs_buffer_len,)+image_shape,dtype=np.float32)
        self.critic_obs = np.zeros(9,dtype=np.float32)

        self.webots_conf = read_config(env_conf_path)

        assert process_idx < arg_worker
        self.env,_ = general_env(env_id="Benchmark",env_conf=env_conf,arg_worker=arg_worker,process_idx=process_idx,asymmetric=True)
        self.state = None
        
        ## Config 
        self.end_reward = end_reward
        self.test_agent = (process_idx == arg_worker-1) and train
        # only in train mode:read num_step.txt and open tb_logger
        if self.test_agent:
            assert log_dir != None
            self.num_test_dir = os.path.dirname(log_dir)
            self.num_test = f"{self.num_test_dir}/num_test.txt"
            if self.end_reward:
                if os.path.exists(self.num_test):
                    with open(self.num_test,"r") as file:
                        data = file.read()
                        print(f"Loading log from iteration: {data}")
                    self.reward_idx = int(data)
            else:
                print(f"Start New train!")
                self.reward_idx = 0
                with open(self.num_test,"w") as file:
                    file.write("0")
            self.init_reward_idx = deepcopy(self.reward_idx)
            self.episode_steps = 0

            ## tb logger
            self.use_tb = use_tb
            if self.use_tb:
                assert log_dir != None
                self.tb_logger = SummaryWriter(log_dir=log_dir)
            self.total_reward = 0
    
    def reset(self,seed=None):
        reset_info={}

        ## Manage State:{"actor_obs":self.actor_obs,"critic_obs":self.critic_obs}
        self.state,_ = self.env.reset() # self.state = {"image"curr_image,"vector":vertor9d}
        curr_image = self.state["image"] # shape:(3,84,84)
        self.actor_obs = np.repeat(curr_image[np.newaxis, :, :, :], 3, axis=0)
        self.critic_obs = self.state["vector"]
        self.actual_state = {"actor_obs":self.actor_obs,"critic_obs":self.critic_obs}

        ## Update tb_logger and num_test.txt file
        if self.test_agent:
            self.reward_idx += self.episode_steps
            if self.reward_idx != self.init_reward_idx and self.use_tb:
                self.tb_logger.add_scalar('Reward', self.total_reward, self.reward_idx)
                self.total_reward = 0
            with open(self.num_test,"w") as file:
                file.write(str(self.reward_idx))
            print(f"Write: {self.reward_idx}")
            self.episode_steps = 0
        return self.actual_state,reset_info
    
    def step(self, action):
        info = {}
        self.state,reward,done,SuppleInfo = self.env.step(action=action)
        
        ## update episode steps
        if self.test_agent:
            self.episode_steps += 1

        ## Manage Actor/Critic Observation
        curr_img = self.state["image"]
        curr_vec = self.state["vector"]
        self.actor_obs = np.roll(self.actor_obs, shift=1, axis=0)
        self.actor_obs[0] = curr_img
        self.critic_obs = curr_vec
        self.actual_state = {"actor_obs":self.actor_obs,"critic_obs":self.critic_obs}

        ## Manage truncated
        curr_step = self.env.curr_step
        info["SuppleInfo"] = SuppleInfo
        if done and curr_step < self.webots_conf["Train_Total_Steps"]:
            truncated = True
        else:
            truncated = False
        
        ## Manage total reward for tensorboard logger
        if self.test_agent and not done:
            self.total_reward += reward
        
        return self.actual_state,reward,done,truncated,info

    def render(self):
        pass

    def close(self):
        pass

    @classmethod
    def get_action_space(cls):
        conf_json = read_config(CONF)
        env_conf = conf_json["Benchmark"]
        return gymnasium.spaces.Discrete(int(env_conf["Action_dim"]))
    
    @classmethod
    def get_obs_space(cls,obs_buffer_len:int=3):
        conf_json = read_config(CONF)
        env_conf = conf_json["Benchmark"]
        image_shape = (env_conf["State_channel"], env_conf["State_size"], env_conf["State_size"])
        assert obs_buffer_len >= 0 and isinstance(obs_buffer_len,int)
        
        obs_space = gymnasium.spaces.Dict({
            "actor_obs":gymnasium.spaces.Box(low=0,high=1.0,shape=(obs_buffer_len,)+image_shape,dtype=np.float32),
            "critic_obs":gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(9,), dtype=np.float32),
        })
        return obs_space
    
def make_env(n_envs,rank,end_reward:bool = False,log_dir:str=None,obs_buffer_len:int=3,use_tb:bool=False):
    def _init():
        env = DVAT_ENV(
            arg_worker=n_envs,
            process_idx=rank,
            end_reward=end_reward,
            log_dir=log_dir,
            obs_buffer_len=obs_buffer_len,
            use_tb=use_tb)
        return env
    return _init