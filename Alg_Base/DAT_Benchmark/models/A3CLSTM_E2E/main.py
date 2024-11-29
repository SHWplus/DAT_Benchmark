from __future__ import print_function, division
import os
os.environ["OMP_NUM_THREADS"] = "1"
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(grandparent_dir)
sys.path.append(parent_dir)

import argparse
import torch
import torch.multiprocessing as mp
from envs.environment import general_env
from utils import read_config
from model import A3Clstm,A3ClstmE2E
from train import train
from A3CLSTM_E2E.test import test
from shared_optim import SharedRMSprop, SharedAdam
import time

parser = argparse.ArgumentParser(description="A3C")


parser.add_argument(
    "-tm",
    "--train-mode",
    type=str,
    help="config training setting",
    default="Normal"
)

parser.add_argument(
    "-pd",
    "--previlege-dim",
    type=int,
    help="config privilege",
    default=4
)


parser.add_argument("-ld", "--load", help="load a trained model",default=True)

parser.add_argument(
    "-w",
    "--workers",
    type=int,
    default=24,
    help="how many training processes to use (default: 16)",
)
parser.add_argument(
    "-gp",
    "--gpu-ids",
    type=int,
    default=[-1],
    nargs="+",
    help="GPUs to use [-1 CPU only] (default: -1)",
)

parser.add_argument(
    "-epi",
    "--epsilon",
    type=float,
    default=0.9,
    help="Epsilon Param for epsilon greedy policy",
)

parser.add_argument(
    "-hs",
    "--hidden-size",
    type=int,
    default=256,
    help="LSTM Cell number of features in the hidden state h",
)
parser.add_argument(
    "-ev",
    "--env",
    default="Benchmark",
    help="environment to train on (default: Benchmark)",
)
parser.add_argument(
    "-model",
    "--model_type",
    type=str,
    default = "E2E",
    help="type the model Type:Default or E2E",
)

parser.add_argument(
    "-Mode",
    "--Mode",
    type=int,
    default=1,
    help="specify train mode(1) or test mode(0)",
)

parser.add_argument(
    "-TP",
    "--Test_Param",
    type=str,
    default="Benchmark",
    help="specify train mode(1) or test mode(0)",
)

parser.add_argument(
    "-Sc",
    "--Scene",
    type=str,
    default="citystreet",
    help="[citystreet,downtown,lake,village,desert,farmland]",
)

parser.add_argument(
    "-W",
    "--Weather",
    type=str,
    default="day",
    help="[day,night,foggy,snow]",
)

parser.add_argument(
    "-P",
    "--Port",
    type=int,
    default=-1,
    help="Communication Port -1 for normal",
)

parser.add_argument(
    "-F",
    "--Freq",
    type=int,
    default=125,
    help="Control Frequency",
)

parser.add_argument(
    "-D",
    "--delay",
    type=int,
    default=20,
    help="Delay after webots start",
)

parser.add_argument(
    "-N",
    "--New_Train",
    action='store_true',
    default=False,
    help="Whether restart a new training",
)

parser.add_argument(
    "-ver",
    "--verbose",
    action='store_true',
    default=False,
    help="Whether need verbose",
)

parser.add_argument(
    "-l", "--lr", type=float, default=0.0001, help="learning rate (default: 0.0001)"
)
parser.add_argument(
    "-ec",
    "--entropy-coef",
    type=float,
    default=0.01,
    help="entropy loss coefficient (default: 0.01)",
)
parser.add_argument(
    "-vc",
    "--value-coef",
    type=float,
    default=0.5,
    help="value coefficient (default: 0.5)",
)
parser.add_argument(
    "-g",
    "--gamma",
    type=float,
    default=0.99,
    help="discount factor for rewards (default: 0.99)",
)
parser.add_argument(
    "-t", "--tau", type=float, default=1.00, help="parameter for GAE (default: 1.00)"
)
parser.add_argument(
    "-s", "--seed", type=int, default=1, help="random seed (default: 1)"
)

parser.add_argument(
    "-ns",
    "--num-steps",
    type=int,
    default=20,
    help="number of forward steps in A3C (default: 20)",
)
parser.add_argument(
    "-mel",
    "--max-episode-length",
    type=int,
    default=10000,
    help="maximum length of an episode (default: 10000)",
)
parser.add_argument(
    "-so",
    "--shared-optimizer",
    default=True,
    help="use an optimizer with shared statistics.",
)

parser.add_argument(
    "-sm",
    "--save-max",
    help="Save model on every test run high score matched or bested",
    default=False
)
parser.add_argument(
    "-o",
    "--optimizer",
    default="Adam",
    choices=["Adam", "RMSprop"],
    help="optimizer choice of Adam or RMSprop",
)
parser.add_argument(
    "-lmi",
    "--load-model-dir",
    default="./models/A3CLSTM_E2E/trained_models/",
    help="folder to load trained models from",
)

parser.add_argument(
    "-lmd",
    "--load-model-idx",
    default=-1,
    help="idx of the trained model to load( Default=-1:load the last file weight in last training)",
)

parser.add_argument(
    "-smd",
    "--save-model-dir",
    default="./models/A3CLSTM_E2E/trained_models/",
    help="folder to save trained models",
)
parser.add_argument("-lg", "--log-dir", default="./models/A3CLSTM_E2E/E2E_logs/", help="folder to save logs")

parser.add_argument(
    "-a", "--amsgrad", action="store_true", help="Adam optimizer amsgrad parameter"
)
parser.add_argument(
    "--skip-rate",
    type=int,
    default=4,
    metavar='SR',
    help="frame skip rate (default: 4)")

parser.add_argument(
    "-tl",
    "--tensorboard-logger",
    default=True,
    help="Creates tensorboard logger to see graph of model, view model weights and biases, and monitor test agent reward progress",
)
parser.add_argument(
    "-evc", "--env-config",
    default="./config.json",
    help="environment to crop and resize info (default: config.json)")
parser.add_argument(
    "-dss",
    "--distributed-step-size",
    type=int,
    default=[],
    nargs="+",
    help="use different step size among workers by using a list of step sizes to distributed among workers to use (default: [])",
)

parser.add_argument(
    "-TM",
    "--Test_Mode",
    type=str,
    default="CR",
    help="Choose Metrics of performence: CR or TSR",
)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.Mode == 0:
        MODE = "test"
    else:
        MODE = "train"

    if args.Port == -1:
        import socket

        sock = socket.socket()
        sock.bind(("", 0))
        _, args.Port = sock.getsockname()
        sock.close()

    import json

    with open(
        "../../Webots_Simulation/traffic_project/config/env_config.json", "r"
    ) as file:
        data = json.load(file)
    data["Config_Agen_Num_Port"] = args.Port
    data["Control_Frequence"] = args.Freq
    data["Verbose"] = False
    if MODE == "test":
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
        
        data["No_Reward_Done_Steps"] = 10000
    elif MODE == "train":
        data["Simulation_Mode"]="train"
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
    with open(
        "../../Webots_Simulation/traffic_project/config/env_config.json", "w"
    ) as file:
        json.dump(data, file, indent=4)

    with open(
        "./config.json", "r"
    ) as file:
        data = json.load(file)

    data["Benchmark"]["auto_start"]=True
    data["Benchmark"]["scene"]=args.Scene
    data["Benchmark"]["weather"]=args.Weather
    data["Benchmark"]["port_process"] = args.Port
    data["Benchmark"]["Control_Frequence"] = args.Freq
    data["Benchmark"]["delay"] = args.delay
    data["Benchmark"]["verbose"] = args.verbose

    # Set the reward type
    if MODE == "train":
        data["Benchmark"]["RewardType"] = "E2E"
    elif MODE == "test":
        data["Benchmark"]["RewardType"] = "default"

    with open(
        "./config.json", "w"
    ) as file:
        json.dump(data, file, indent=4)

    if args.New_Train and os.path.exists("./models/A3CLSTM_E2E/num_test.txt"):
        with open(
            "./models/A3CLSTM_E2E/num_test.txt", "w"
        ) as file:
            file.write("0")

    if MODE == "train":
        import subprocess
        tb = subprocess.Popen(
            ["tensorboard --logdir ./models/A3CLSTM_E2E/runs/Benchmark_training"],
            shell=True,
        )

    torch.manual_seed(args.seed)
    if args.gpu_ids != [-1]:
        torch.cuda.manual_seed(args.seed)
        mp.set_start_method("spawn")
    setup_json = read_config(args.env_config)
    for i in setup_json.keys():
        if i in args.env:
            env_conf = setup_json[i]
    if args.model_type == "Default":
        shared_model = A3Clstm(env_conf["State_channel"], env_conf["Action_dim"], args)
    elif args.model_type == "E2E":
        shared_model = A3ClstmE2E(env_conf["State_channel"], env_conf["Action_dim"], args)
    if args.load and os.path.exists(f"{args.save_model_dir}{args.env}.dat") and MODE == "train" and not args.New_Train:
        print("Loading Model: "+f"{args.load_model_dir}{args.env}.dat")
        saved_state = torch.load(
            f"{args.load_model_dir}{args.env}.dat",
            map_location=lambda storage, loc: storage,
        )
        shared_model.load_state_dict(saved_state)
    shared_model.share_memory()

    if args.shared_optimizer:
        if args.optimizer == 'RMSprop':
            optimizer = SharedRMSprop(shared_model.parameters(), lr=args.lr)
        if args.optimizer == 'Adam':
            optimizer = SharedAdam(
                shared_model.parameters(), lr=args.lr, amsgrad=args.amsgrad)
        optimizer.share_memory()
    else:
        optimizer = None

    if MODE == "train":
        processes = []
        p = mp.Process(target=test, args=(args, shared_model, env_conf))
        p.start()
        processes.append(p)
        time.sleep(0.001)
        for rank in range(0, args.workers-1):
            p = mp.Process(
                target=train, args=(rank, args, shared_model, optimizer, env_conf))
            p.start()
            processes.append(p)
            time.sleep(0.001)
        for p in processes:
            time.sleep(0.001)
            p.join()
    else:
        load_path = "./models/A3CLSTM_E2E/trained_models/"
        path_list = [args.Test_Param+".dat"]
        processes = []
        for idx,dat in enumerate(path_list):
            p = mp.Process(target=test, args=(args, shared_model, env_conf,False,load_path+dat,len(path_list),idx))
            p.start()
            processes.append(p)
            time.sleep(0.001)
        for p in processes:
            time.sleep(0.001)
            p.join()