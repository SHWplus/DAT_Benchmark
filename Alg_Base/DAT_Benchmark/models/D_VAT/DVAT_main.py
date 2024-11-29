import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
sys.path.append(grandparent_dir)

from tianshou.env import SubprocVectorEnv
from tianshou.policy import RandomPolicy
from tianshou.data import Collector, VectorReplayBuffer
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import gymnasium

from DVAT_envs import make_env,DVAT_ENV
from envs.async_vecenv_ts import SubprocVectorEnv_TS,TS_Collector
import subprocess, time
import argparse
from denseMlpPolicy import create_sacd_policy,get_action
from envs.gym_envs import ENV_CONF


def DVAT_train(args):

    simulator = subprocess.Popen(
        ["webots --no-rendering --mode=fast ../../Webots_Simulation/traffic_project/worlds/" + args.map],
        shell=True,
    )
    time.sleep(args.delay)

    settings = {
        'n_timesteps': 10000000,
        'batch_size': 64,
        'buffer_size': 10000,
        'train_freq': 8,
    }

    # create parallel envs
    if args.New_Train:
        end_reward = False
    else:
        end_reward = True
    
    if args.tensorboard_port != -1:
        # create tb_logger
        tensorboard_logdir = "./models/D_VAT/DVAT_logs"
        if tensorboard_logdir is None:
            os.makedirs(tensorboard_logdir)
        envs = [make_env(n_envs=args.workers,rank=i,end_reward=end_reward,log_dir=tensorboard_logdir,use_tb=True) for i in range(args.workers)]
        tb = subprocess.Popen(
            ["tensorboard --logdir "+tensorboard_logdir],
            shell=True,
        )
    else:
        envs = [make_env(n_envs=args.workers,rank=i,end_reward=end_reward,log_dir=tensorboard_logdir,use_tb=False) for i in range(args.workers)]

    vector_env = SubprocVectorEnv_TS(envs)
    ## create policy
    action_space = DVAT_ENV.get_action_space()
    obs_space = DVAT_ENV.get_obs_space()
    actor_obs_space = obs_space["actor_obs"]
    critic_obs_space = obs_space["critic_obs"]
    
    sacd_policy = create_sacd_policy(actor_obs_space=actor_obs_space,action_space=action_space,obs_shape_critic=critic_obs_space.shape[0],action_shape=int(action_space.n))
    sacd_policy.is_within_training_step = True

    ## load model
    Load_Model = not args.New_Train

    if Load_Model:
        if os.path.exists(args.savepath):
            try:
                sacd_policy.load_state_dict(torch.load(args.savepath))
                print(f"Load pretrained weight success!")
            except Exception as e:
                print(f"Load pretrain weight failed: {e}")
        else:
            print(f"weight path {args.savepath} not exists!")


    ## create buffer
    buffer = VectorReplayBuffer(total_size=settings["buffer_size"],buffer_num=args.workers)

    ## create collector
    collector = TS_Collector(sacd_policy, vector_env, buffer)
    collected_steps = 0

    # get device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    result = collector.collect(n_step=settings["train_freq"],reset_before_collect=True)
    
    save_interval = 10
    while collected_steps < settings["n_timesteps"]:
        try:
            # sample data from env
            result = collector.collect(n_step=settings["train_freq"])
            collected_steps += settings["train_freq"]

            batch_buffer,batch_indices = collector.buffer.sample(settings["batch_size"])
            collected_steps += 1
                
            batch_buffer.act = torch.tensor(batch_buffer.act).to(device) if isinstance(batch_buffer.act, np.ndarray) else batch_buffer.act
            batch_buffer.obs = {k: torch.tensor(v).to(device) if isinstance(v, np.ndarray) else v for k, v in batch_buffer.obs.items()}
            batch_buffer.obs_next = {k: torch.tensor(v).to(device) if isinstance(v, np.ndarray) else v for k, v in batch_buffer.obs_next.items()}
            batch_buffer.rew = torch.tensor(batch_buffer.rew).to(device) if isinstance(batch_buffer.rew, np.ndarray) else batch_buffer.rew

            target_q = sacd_policy._target_q(collector.buffer, indices=batch_indices)
            losses = sacd_policy.learn(batch=batch_buffer,target_q=target_q)

            if collected_steps % save_interval == 0:
                torch.save(sacd_policy.state_dict(),args.savepath)
        finally:
            tb.terminate()
            simulator.terminate()
            try:
                tb.wait(timeout=5)
                simulator.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tb.kill()
                simulator.kill()

def DVAT_test(args):

    simulator = subprocess.Popen(
        ["webots --no-rendering --mode=fast ../../Webots_Simulation/traffic_project/worlds/" + args.map],
        shell=True,
    )
    time.sleep(args.delay)

    # test mode test 1 agent per time
    env = DVAT_ENV(arg_worker=1, process_idx=0, end_reward=False, log_dir=None, obs_buffer_len=3,train=False)

    # create sacd policy
    sacd_policy = create_sacd_policy(
        actor_obs_space=env.observation_space['actor_obs'],
        action_space=env.action_space,
        obs_shape_critic=env.observation_space['critic_obs'].shape[0],
        action_shape=int(env.action_space.n)
    )
    
    # load model state dict
    if not os.path.exists(args.savepath):
        raise FileNotFoundError(f"weight path: {args.savepath} not exists!")
    sacd_policy.load_state_dict(torch.load(args.savepath))
    print(f"Load pretrained weight success!")

    # set policy as evaluation mode
    sacd_policy.eval()

    # reset env and get init state
    state, _ = env.reset()

    total_reward_list = []
    episode_reward = 0
    done = False

    # run test
    while len(total_reward_list) < args.test_length:
        try:
            if not done:
                action = get_action(sacd_policy,state)
                state, reward, done, _, _ = env.step(action)
                episode_reward += reward
            if done:
                if episode_reward != 0:
                    if args.Test_Mode == "CR":
                        total_reward_list.append(episode_reward)
                        real_matrics = episode_reward
                    elif args.Test_Mode == "TSR":
                        with open(
                            ENV_CONF, "r"
                        ) as file:
                            data_env = json.load(file)
                        total_steps = data_env["Train_Total_Steps"]
                        control_freq = data_env["Control_Frequence"]
                        max_reward = total_steps*control_freq/500
                        real_matrics = episode_reward/max_reward
                        total_reward_list.append(real_matrics)
                    print(f"finish episode:{len(total_reward_list)} episode_reward:{episode_reward} reward:{real_matrics}")
                    episode_reward = 0
                    done=False
                    state, _ = env.reset()
                else:
                    state, _ = env.reset()
                    episode_reward = 0
                    done=False
        except Exception as e:
            print(f"An error Occur:{e}")
        finally:
            simulator.terminate()
            try:
                simulator.wait(timeout=5)
            except subprocess.TimeoutExpired:
                simulator.kill()


    # output xlsx file
    total_reward_list.append(
        f"{np.mean(total_reward_list):.3f}±{np.std(total_reward_list):.3f}"
    )
    import pandas as pd
    df = pd.DataFrame(total_reward_list, columns=["Values"])
    map_name = args.map.rsplit('.', 1)[0]
    df.to_excel(f"./models/D_VAT/DVAT_logs/test_{map_name}.xlsx", index=False)

if __name__ == "__main__":
    # --------------------------------------------------parameter-----------------------------------------------
    parse = argparse.ArgumentParser(description="run DVAT")
    parse.add_argument(
        "-w",
        "--workers",
        default=2,
        type=int,
        metavar="",
        help="the number of agents, default: 24",
    )
    parse.add_argument(
        "-t",
        "--train_mode",
        default=1,
        type=int,
        metavar="",
        help="whether to enable training mode, default: 1",
    )
    parse.add_argument(
        "-p",
        "--port",
        default=-1,
        type=int,
        metavar="",
        help="the communication port between the algorithm and the simulator, keep this parameter to default -1, it will automatically find an available port.",
    )
    parse.add_argument(
        "-params",
        "--savepath",
        default="./models/D_VAT/params.pth",
        type=str,
        metavar="",
        help="model parameter filename, default: ./models/D_VAT/params.pth",
    )
    parse.add_argument(
        "-m",
        "--map",
        default="citystreet-day.wbt",
        type=str,
        metavar="",
        help="the filename of map, default: citystreet-day.wbt",
    )
    parse.add_argument(
        "-tp",
        "--tensorboard_port",
        default=6006,
        type=int,
        metavar="",
        help="the port of tensorboard, default: 6006. (if -1 TensorBoard disabled). Set to any other value to enable TensorBoard, which will find an available port if needed.",
    )

    parse.add_argument(
        "-N",
        "--New_Train",
        action="store_true",
        default=False,
        help="whether restart a new training, default: False",
    )

    parse.add_argument(
        "-Len",
        "--observation_buffer_length",
        type=int,
        default=3,
        help="number of frame use for state",
    )

    parse.add_argument(
        "-tl",
        "--test_length",
        type=int,
        default=10,
        help="number of episodes for test",
    )
    parse.add_argument(
        "-D",
        "--delay",
        type=int,
        default=20,
        help="Delay after webots start",
    )
    parse.add_argument(
        "-ver",
        "--verbose",
        action='store_true',
        default=False,
        help="Whether need verbose",
    )
    parse.add_argument(
        "-TM",
        "--Test_Mode",
        type=str,
        default="CR",
        help="Choose Metrics of performence: CR or TSR",
    )
    args = parse.parse_args()

    if args.port == -1:
        import socket

        sock = socket.socket()
        sock.bind(("", 0))
        _, args.port = sock.getsockname()
        sock.close()

    import json

    # ------------------------------env_config.json--------------------------------
    with open(
        "../../Webots_Simulation/traffic_project/config/env_config.json", "r"
    ) as file:
        data = json.load(file)
    data["Config_Agen_Num_Port"] = args.port
    data["Simulation_Mode"] = "train"
    data["Tracker_Def"] = "DRONE"
    data["Sumo_Params"]["rou_update"] = True
    data["Verbose"] = False
    if args.train_mode == 1:
        data["Drone_Random_Config"]["direction_random"] = False
        data["Drone_Random_Config"]["direction_fixed"] = 0

        data["Drone_Random_Config"]["view_pitch_random"] = False
        data["Drone_Random_Config"]["view_pitch_fixed"] = 1.37

        data["Drone_Random_Config"]["height_random"] = False
        data["Drone_Random_Config"]["height_fixed"] = 22

        data["Drone_Random_Config"]["horizon_bias_random"] = False
        data["Drone_Random_Config"]["horizon_bias_fixed"] = 0

        data["Drone_Random_Config"]["verticle_bias_random"] = False
        data["Drone_Random_Config"]["verticle_bias_fixed"] = 0

        data["Sumo_Params"]["fixed_color"] = False
        data["Sumo_Params"]["fixed_seed"] = False
        data["Sumo_Params"]["fixed_car_group_num"] = False

        data["Reward_Config"]["view_range"] = 1

        data["No_Reward_Done_Steps"] = 10000 # forbid no reward done setting

    else:
        data["Simulation_Mode"]="train"
        data["Drone_Random_Config"]["direction_random"] = False

        data["Drone_Random_Config"]["view_pitch_random"] = False
        data["Drone_Random_Config"]["view_pitch_fixed"] = 1.37

        data["Drone_Random_Config"]["height_random"] = False
        data["Drone_Random_Config"]["height_fixed"] = 22

        data["Drone_Random_Config"]["horizon_bias_random"] = False
        data["Drone_Random_Config"]["horizon_bias_fixed"] = 0

        data["Drone_Random_Config"]["verticle_bias_random"] = False
        data["Drone_Random_Config"]["verticle_bias_fixed"] = 0

        data["Sumo_Params"]["fixed_color"] = False
        data["Sumo_Params"]["fixed_seed"] = True
        data["Sumo_Params"]["fixed_car_group_num"] = True
        
        data["No_Reward_Done_Steps"] = 10000
        if args.Test_Mode == "CR":
            data["Reward_Config"]["reward_type"] = "view"
            data["Reward_Config"]["reward_mode"] = "continuous"
            data["Reward_Config"]["view_range"] = 1
        elif args.Test_Mode == "TSR":
            data["Reward_Config"]["reward_type"] = "view"
            data["Reward_Config"]["reward_mode"] = "discrete"
            data["Reward_Config"]["view_range"] = 1
        else:
            raise ValueError(f"Invalid Test_Mode: {args.Test_Mode}. Expected one of ['CR','TSR']")
        
    with open(
        "../../Webots_Simulation/traffic_project/config/env_config.json", "w"
    ) as file:
        json.dump(data, file, indent=4)

    # ------------------------------config.json--------------------------------
    with open("config.json", "r") as file:
        data = json.load(file)
    data["Benchmark"]["port_process"] = args.port
    data["Benchmark"]["auto_start"] = False
    data["Benchmark"]["verbose"] = args.verbose
    if args.train_mode == 1:
        data["Benchmark"]["RewardType"] = "DVAT"
    else:
        data["Benchmark"]["RewardType"] = "default"
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

    if args.New_Train and os.path.exists("./models/D_VAT/DVAT_logs/steps.txt"):
        with open("./models/D_VAT/DVAT_logs/steps.txt", "w") as file:
            file.write("0")

    if args.train_mode == 1:
        DVAT_train(args)
    if args.train_mode == 0:
        DVAT_test(args)



