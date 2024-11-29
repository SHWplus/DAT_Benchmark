from __future__ import division
import os
os.environ["OMP_NUM_THREADS"] = "1"
from setproctitle import setproctitle as ptitle
import torch
from envs.environment import general_env
from utils import setup_logger
from model import A3Clstm,A3ClstmE2E
from player_util import Agent
from torch.autograd import Variable
import time
import logging
from utils import get_mean_std
import pandas as pd


TEST_NUM = 10
EXCEL = True

def test(args, shared_model, env_conf,read_num_test:bool=True,load_path:str=None,num_worker:int=1,process_idx:int=0):
    ptitle("Test Agent")
    gpu_id = args.gpu_ids[-1]
    setup_logger(f"{args.env}_log", rf"{args.log_dir}{args.env}_log")

    torch.manual_seed(args.seed)
    if gpu_id >= 0:
        torch.cuda.manual_seed(args.seed)
    if read_num_test:
        env,process_func = general_env(args.env, env_conf,args.workers,process_idx=args.workers-1)
    else:
        print(f"number worker: {num_worker} process_idx: {process_idx}")
        env,process_func = general_env(args.env, env_conf,num_worker,process_idx=process_idx)
    reward_sum = 0
    start_time = time.time()
    num_tests = 0
    reward_total_sum = 0
    player = Agent(None, env, args, None,process_func)
    player.gpu_id = gpu_id

    if args.model_type == "Default":
        player.model = A3Clstm(env_conf["State_channel"], env_conf["Action_dim"], args)
    elif args.model_type == "E2E":
        player.model = A3ClstmE2E(env_conf["State_channel"], env_conf["Action_dim"], args)
        
    if args.tensorboard_logger:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(f"models/A3CLSTM_E2E/runs/{args.env}_training")
        writer.close()

    if args.Test_Mode == "TSR":
        import json
        with open(
            "../../Webots_Simulation/traffic_project/config/env_config.json", "r"
        ) as file:
            data = json.load(file)
        highest_score = data["Train_Total_Steps"]/(500/data["Control_Frequence"])

    player.state,player.suppleinfo = player.env.reset()
    if args.train_mode == "privilege":
        player.privilegeinfo = player.int2one_hot(int(player.suppleinfo[0][-1]),args.previlege_dim)
    player.state = process_func(state=player.state,env = player.env)
    if gpu_id >= 0:
        with torch.cuda.device(gpu_id):
            player.model = player.model.cuda()
            player.state = torch.from_numpy(player.state).float().cuda()
    else:
        player.state = torch.from_numpy(player.state).float()

    num_test_path = "./models/A3CLSTM_E2E/num_test.txt"
    if os.path.exists(num_test_path) and read_num_test:
        with open(num_test_path, "r") as file:
            data = file.read()
        file.close()
        num_tests = int(data)

    reward_list = []
    max_score = 0
    num_step = 0
    num_episode = 0
    if not read_num_test:
        player.model.load_state_dict(torch.load(load_path))
        print(f"Loading State dict: {load_path}")
        filename = os.path.basename(load_path)  
        filename_without_ext = os.path.splitext(filename)[0]
    try:
        while 1:
            if player.done and read_num_test:
                if gpu_id >= 0:
                    with torch.cuda.device(gpu_id):
                        player.model.load_state_dict(shared_model.state_dict())
                else:
                    player.model.load_state_dict(shared_model.state_dict())
            player.action_test()
            num_step += 1
            reward_sum += player.reward
            if player.done:
                if reward_sum != 0:
                    num_tests += num_step
                    num_episode += 1
                    print(f"num_episode: {num_episode}")
                    reward_total_sum += reward_sum
                    reward_mean = reward_total_sum / num_tests
                    if not read_num_test:
                        if args.Test_Mode == "AR":
                            reward_list.append(reward_sum)
                            print(f"Episode {len(reward_list)} test accumulated reward:{reward_sum}")
                        elif args.Test_Mode == "TSR":
                            tsr = reward_sum / highest_score
                            reward_list.append(tsr)
                            print(f"Episode {len(reward_list)} test tacking success rate:{tsr}")
                            print(f"check: {highest_score}")
                        if len(reward_list) == TEST_NUM:
                            mean,std = get_mean_std(reward_list)
                            if not EXCEL:
                                print(f"reward_list for {filename_without_ext}: ")
                                for reward in reward_list:
                                    print(f"{reward:.3f}")
                                print(f"{mean:.3f}±{std:.3f}")
                            else:
                                reward_list.append(f"{mean:.3f}±{std:.3f}")
                                df = pd.DataFrame(reward_list, columns=["Values"])
                                df.to_excel(f"./models/A3CLSTM_E2E/{filename[:-4]}.xlsx", index=False)

                if args.tensorboard_logger:
                    if read_num_test:
                        writer.add_scalar(
                            f"{args.env}_Episode_Rewards", reward_sum, num_tests
                        )
                        for name, weight in player.model.named_parameters():
                            writer.add_histogram(name, weight, num_tests)
                    else:
                        writer.add_scalar(
                            f"{args.env}_Episode_Rewards_"+filename_without_ext, reward_sum, num_tests
                        )
                if read_num_test:
                    with open(num_test_path,"w") as file:
                        file.write(str(num_tests))
                    file.close()
                num_step = 0
                if (args.save_max and reward_sum >= max_score) or not args.save_max and read_num_test:
                    if reward_sum >= max_score:
                        max_score = reward_sum
                    if gpu_id >= 0:
                        with torch.cuda.device(gpu_id):
                            state_to_save = player.model.state_dict()
                            torch.save(
                                state_to_save, f"{args.save_model_dir}{args.env}.dat"
                            )
                    else:
                        state_to_save = player.model.state_dict()
                        torch.save(
                            state_to_save, f"{args.save_model_dir}{args.env}.dat"
                        )

                reward_sum = 0
                player.eps_len = 0
                state,player.suppleinfo = player.env.reset()
                if args.train_mode == "privilege":
                    player.privilegeinfo = player.int2one_hot(int(player.suppleinfo[0][-1]),args.previlege_dim)
                state = process_func(state = state,env=player.env)
                if gpu_id >= 0:
                    with torch.cuda.device(gpu_id):
                        player.state = torch.from_numpy(state).float().cuda()
                else:
                    player.state = torch.from_numpy(state).float()

    except KeyboardInterrupt:
        time.sleep(0.01)
        print("KeyboardInterrupt exception is caught")
    finally:
        print("test agent process finished")
        if args.tensorboard_logger:
            writer.close()
