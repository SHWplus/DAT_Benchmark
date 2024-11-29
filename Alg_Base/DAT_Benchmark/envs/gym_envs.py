import gym
from gym import spaces
import gymnasium
import gymnasium.spaces
import numpy as np
from environment import general_env
from utils import read_config
from stable_baselines3.common.monitor import Monitor
from async_vecenv import ASYNC_SubprocVecEnv
from torch.utils.tensorboard import SummaryWriter
import os
from copy import deepcopy
import sys

CONF = "./config.json"
ENV_CONF = "../../Webots_Simulation/traffic_project/config/env_config.json"

class UAV_VAT(gym.Env):
    def __init__(self,arg_worker:int=1,conf_path:str=CONF,env_conf_path:str=ENV_CONF,process_idx:int=0,end_reward:bool = False,log_dir:str=None,obs_buffer_len:int=0) -> None:
        super(UAV_VAT,self).__init__()
        conf_json = read_config(conf_path)
        env_conf = conf_json["Benchmark"] # env_conf:dict

        self.action_space = spaces.Discrete(int(env_conf["Action_dim"]))
        assert obs_buffer_len >= 0 and isinstance(obs_buffer_len,int)
        if obs_buffer_len == 0:
            self.observation_space = spaces.Box(low=0,high=1.0,shape=(env_conf["State_channel"],env_conf["State_size"],env_conf["State_size"]),dtype=np.float32)
        else:
            self.observation_space = spaces.Box(low=0,high=1.0,shape=(obs_buffer_len,env_conf["State_channel"],env_conf["State_size"],env_conf["State_size"]),dtype=np.float32)
        
        self.webots_conf = read_config(env_conf_path)

        assert process_idx < arg_worker
        self.env,_ = general_env(env_id="Benchmark",env_conf=env_conf,arg_worker=arg_worker,process_idx=process_idx)
        self.state = None

        self.end_reward = end_reward and process_idx == arg_worker-1
        if self.end_reward:
            assert log_dir != None
            self.num_test_dir = os.path.dirname(log_dir)
            self.num_test = f"{self.num_test_dir}/num_test.txt"
            if os.path.exists(self.num_test):
                with open(self.num_test,"r") as file:
                    data = file.read()
                    print(f"Read: {data}")
                file.close()
                self.reward_idx = int(data)
            else:
                self.reward_idx = 0
            self.init_reward_idx = deepcopy(self.reward_idx)
            self.tb_logger = SummaryWriter(log_dir=log_dir)
            self.total_reward = 0
            
    
    def reset(self):
        self.state,_ = self.env.reset()
        if self.end_reward:
            if self.reward_idx != self.init_reward_idx:
                self.tb_logger.add_scalar('Reward', self.total_reward, self.reward_idx)
                self.total_reward = 0
            self.reward_idx += 1
            with open(self.num_test,"w") as file:
                file.write(str(self.reward_idx))
                print(f"Write: {self.reward_idx}")
            file.close()
        return self.state
    
    def step(self, action):
        info = {}
        self.state,reward,done,SuppleInfo = self.env.step(action=action)
        curr_step = self.env.curr_step
        if done and curr_step < self.webots_conf["Train_Total_Steps"]:
            info["TimeLimit.truncated"] = True
        else:
            info["TimeLimit.truncated"] = False

        if self.end_reward and not done:
            self.total_reward += reward
        
        return self.state,reward,done,info

    def render(self):
        pass

    def close(self):
        pass

    @classmethod
    def get_action_space(cls):
        conf_json = read_config(CONF)
        env_conf = conf_json["Benchmark"]
        return spaces.Discrete(int(env_conf["Action_dim"]))


class UAV_VAT_Gymnasium(gymnasium.Env):
    def __init__(self,arg_worker:int=1,conf_path:str=CONF,env_conf_path:str=ENV_CONF,process_idx:int=0,end_reward:bool = False,log_dir:str=None,obs_buffer_len:int=0) -> None:
        super(UAV_VAT_Gymnasium,self).__init__()
        conf_json = read_config(conf_path)
        env_conf = conf_json["Benchmark"] # env_conf:dict

        self.action_space = gymnasium.spaces.Discrete(int(env_conf["Action_dim"]))
        assert obs_buffer_len >= 0 and isinstance(obs_buffer_len,int)
        if obs_buffer_len == 0:
            self.observation_space = gymnasium.spaces.Box(low=0,high=1.0,shape=(env_conf["State_channel"],env_conf["State_size"],env_conf["State_size"]),dtype=np.float32)
        else:
            self.observation_space = gymnasium.spaces.Box(low=0,high=1.0,shape=(obs_buffer_len,env_conf["State_channel"],env_conf["State_size"],env_conf["State_size"]),dtype=np.float32)

        self.webots_conf = read_config(env_conf_path)

        assert process_idx < arg_worker
        self.env,_ = general_env(env_id="Benchmark",env_conf=env_conf,arg_worker=arg_worker,process_idx=process_idx)
        self.state = None
        
        self.end_reward = end_reward and process_idx == arg_worker-1
        if self.end_reward:
            assert log_dir != None
            self.num_test_dir = os.path.dirname(log_dir)
            self.num_test = f"{self.num_test_dir}/num_test.txt"
            if os.path.exists(self.num_test):
                with open(self.num_test,"r") as file:
                    data = file.read()
                    print(f"Read: {data}")
                file.close()
                self.reward_idx = int(data)
            else:
                self.reward_idx = 0
            self.init_reward_idx = deepcopy(self.reward_idx)
            self.tb_logger = SummaryWriter(log_dir=log_dir)
            self.total_reward = 0
    
    def reset(self,seed=None):
        reset_info={}
        self.state,_ = self.env.reset()
        if self.end_reward:
            if self.reward_idx != self.init_reward_idx:
                self.tb_logger.add_scalar('Reward', self.total_reward, self.reward_idx)
                self.total_reward = 0
            self.reward_idx += 1
            with open(self.num_test,"w") as file:
                file.write(str(self.reward_idx))
                print(f"Write: {self.reward_idx}")
            file.close()
        return self.state,reset_info
    
    def step(self, action):
        info = {}
        self.state,reward,done,SuppleInfo = self.env.step(action=action)
        curr_step = self.env.curr_step
        info["SuppleInfo"] = SuppleInfo
        if done and curr_step < self.webots_conf["Train_Total_Steps"]:
            truncated = True

        else:
            truncated = False
        
        if self.end_reward and not done:
            self.total_reward += reward
        
        return self.state,reward,done,truncated,info

    def render(self):
        pass

    def close(self):
        pass

    @classmethod
    def get_action_space(cls):
        conf_json = read_config(CONF)
        env_conf = conf_json["Benchmark"]
        return gymnasium.spaces.Discrete(int(env_conf["Action_dim"]))



from gym.envs.registration import register

register(
    id='UAVVAT-v0',
    entry_point='gym_envs:UAV_VAT',
)


def make_env(n_envs,rank,gym=True,monitor=False,end_reward:bool = False,log_dir:str=None,obs_buffer_len:int=0):
    def _init():
        if gym:
            env = UAV_VAT(arg_worker=n_envs,process_idx=rank,end_reward=end_reward,log_dir=log_dir,obs_buffer_len=obs_buffer_len)
            print("Using Gym Environment")
        else:
            env = UAV_VAT_Gymnasium(arg_worker=n_envs,process_idx=rank,end_reward=end_reward,log_dir=log_dir,obs_buffer_len=obs_buffer_len)
            print("Using Gymnasium Environment")
        if monitor:
            env = Monitor(env)
        return env
    return _init

def gym_test():
    import gym
    import numpy as np
	
    env = gym.make('UAVVAT-v0')
    observation = env.reset()

    for _ in range(10000):
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        env.render()

        if done:
            observation = env.reset()

    env.close()

def stableparallel_test(n_envs:int,gym=True,end_reward:bool = False,log_dir:str=None):
    from stable_baselines3 import PPO
    
    # 16 parallel envs for test
    n_envs = n_envs
    env = ASYNC_SubprocVecEnv([make_env(n_envs=n_envs,rank=rank,gym=gym,end_reward=end_reward,log_dir=log_dir) for rank in range(n_envs)])
    tb_logdir = "./envs/PPO_testtb"
    if not os.path.exists(tb_logdir):
        os.makedirs(tb_logdir)
    model = PPO('MlpPolicy', env, verbose=1,tensorboard_log=tb_logdir,n_steps=16)
    model.learn(total_timesteps=100000,log_interval=10) #,callback=CustomCallback
    env.close()

if __name__ == "__main__":
    # gym_test()
    stableparallel_test(n_envs=16,gym=False)



