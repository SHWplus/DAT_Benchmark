import torch
import torch.nn as nn
from torch.distributions.categorical import Categorical
import os
import numpy as np

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(grandparent_dir)
sys.path.append(parent_dir)


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer

class RVAT_Backbone(nn.Module):
    class CN(nn.Module):
        def __init__(self, input_channels):
            super().__init__()
            self.net = nn.Sequential(
                layer_init(nn.Conv2d(input_channels, 16, 8, stride=4)),
                nn.ReLU(inplace=True),
                layer_init(nn.Conv2d(16, 32, 4, stride=2)),
                nn.ReLU(inplace=True),
                nn.Flatten(),
                layer_init(nn.Linear(32 * 9 * 9, 256), std=1),
                nn.ReLU(inplace=True),
            )

        def forward(self, x):
            return self.net(x)

    class GRU(nn.Module):
        def __init__(self, cnn: nn.Module):
            super().__init__()
            self.cnn = cnn
            self.gru = nn.GRUCell(256, 256)
            self.relu = nn.ReLU(inplace=True)

            for name, param in self.gru.named_parameters():
                if "bias" in name:
                    nn.init.constant_(param, 0)
                elif "weight" in name:
                    nn.init.orthogonal_(param, 1.0)

        def get_states(self, x, gru_state, done):
            hidden = self.cnn(x)
            batch_size = gru_state.shape[0]
            hidden = hidden.view((-1, batch_size, self.gru.input_size))
            done = done.view((-1, batch_size))
            new_hidden = []
            for h, d in zip(hidden, done):
                gru_state = self.gru(h, (1.0 - d).view(-1, 1) * gru_state)
                new_hidden += [gru_state]
            return self.relu(torch.cat(new_hidden)), gru_state

    class FC(nn.Module):
        def __init__(self, output_width, std=1):
            super().__init__()
            self.net = nn.Sequential(
                layer_init(nn.Linear(256, 200), std=1),
                nn.ReLU(inplace=True),
                layer_init(nn.Linear(200, 100), std=1),
                nn.ReLU(inplace=True),
                layer_init(nn.Linear(100, output_width), std=std),
            )

        def forward(self, x):
            return self.net(x)

    def __init__(self, input_channels, action_dim=7):
        super().__init__()
        self.actor0, self.actor1 = self.GRU(self.CN(input_channels)), self.FC(
            action_dim, 0.01
        )
        self.critic0, self.critic1 = self.GRU(self.CN(input_channels)), self.FC(1)

    def get_value(self, x, gru_state, done):
        hidden, gru_state = self.critic0.get_states(x, gru_state, done)
        return self.critic1(hidden), gru_state

    def get_action_and_value(self, x, gru_state, done, action=None):
        hidden, gru_state0 = self.actor0.get_states(x, gru_state[0], done)
        probs = Categorical(logits=self.actor1(hidden))
        if action is None:
            action = probs.sample()
        values, gru_state1 = self.get_value(x, gru_state[1], done)
        return (
            action,
            probs.log_prob(action),
            probs.entropy(),
            values,
            torch.stack((gru_state0, gru_state1)),
        )

    def predict_action(self, x, gru_state, done):
        hidden, gru_state = self.actor0.get_states(x, gru_state, done)
        action = torch.argmax(self.actor1(hidden), dim=1)
        return action, gru_state


class RVAT:
    def __init__(self, **kwargs):

        ######################################
        self.device = torch.device("cuda")
        self.envs = None
        self.savepath = "params.pth"

        ####################################args for init
        self.input_channels = 3
        # self.hidden_width = 64
        self.action_dim = 7

        ####################################args for train

        self.num_steps = 50
        self.num_envs = 4
        self.num_minibatches = 2  # factor of num_envs

        self.global_step = 0  # Initialization not supported !!!

        self.lr = 3e-4  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.lamda = 0.95  # GAE parameter
        self.epsilon = 0.2  # PPO clip parameter
        self.K_epochs = 3  # PPO parameter
        self.entropy_coef = 0.01  # Entropy coefficient
        # self.vloss_coef = 0.5
        self.max_grad_norm = 0.5

        self.load = True  # Whether load pretrain weight
        
        self.test_Mode = "CR" # Choose test metrics

        ##################################

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.model = RVAT_Backbone(self.input_channels, self.action_dim).to(self.device)

        if os.path.exists(self.savepath) and self.load == True:
            print("Loading Pretrained weight")
            self.model.load_state_dict(torch.load(self.savepath))

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, eps=1e-5)

    def sample_update(self, next_gru_state, next_state, next_done):  # modify

        # st=time.time()

        initial_gru_state = next_gru_state.clone()

        obs = torch.zeros(
            (self.num_steps, self.num_envs) + (self.input_channels, 84, 84)
        ).to(self.device)

        actions = torch.zeros((self.num_steps, self.num_envs)).to(self.device)

        logprobs = torch.zeros((self.num_steps, self.num_envs)).to(self.device)
        rewards = torch.zeros((self.num_steps, self.num_envs)).to(self.device)
        dones = torch.zeros((self.num_steps, self.num_envs)).to(self.device)
        values = torch.zeros((self.num_steps, self.num_envs)).to(self.device)

        for step in range(self.num_steps):

            self.global_step += self.num_envs

            obs[step] = next_state
            dones[step] = next_done
            with torch.no_grad():
                action, logprob, _, value, next_gru_state = (
                    self.model.get_action_and_value(
                        next_state, next_gru_state, next_done
                    )
                )
                values[step] = value.view(-1)
                actions[step] = action
                logprobs[step] = logprob

            next_state, reward, done = self.envs.step(action.cpu().numpy())
            rewards[step] = torch.Tensor(reward).to(self.device).view(-1)
            next_state = torch.Tensor(next_state).to(self.device)
            next_done = torch.Tensor(done).to(self.device)

        torch.cuda.empty_cache()

        # bootstrap value if not done
        with torch.no_grad():
            next_value = self.model.get_value(next_state, next_gru_state[1], next_done)[
                0
            ].view(1, -1)

            advantages = torch.zeros_like(rewards).to(self.device)
            lastgaelam = 0
            for t in reversed(range(self.num_steps)):
                if t == self.num_steps - 1:
                    nextnonterminal = 1.0 - next_done
                    nextvalues = next_value
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    nextvalues = values[t + 1]
                delta = (
                    rewards[t] + self.gamma * nextvalues * nextnonterminal - values[t]
                )
                advantages[t] = lastgaelam = (
                    delta + self.gamma * self.lamda * nextnonterminal * lastgaelam
                )

            returns = advantages + values

        obs = obs.view((-1,) + (self.input_channels, 84, 84))
        logprobs = logprobs.view(-1)
        actions = actions.view((-1,))
        dones = dones.view(-1)
        advantages = advantages.view(-1)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        returns = returns.view(-1)
        values = values.view(-1)

        envsperbatch = self.num_envs // self.num_minibatches
        envinds = np.arange(self.num_envs)
        flatinds = np.arange(self.num_steps * self.num_envs).reshape(
            self.num_steps, self.num_envs
        )
        for epoch in range(self.K_epochs):
            np.random.shuffle(envinds)
            for start in range(0, self.num_envs, envsperbatch):

                end = start + envsperbatch
                mbenvinds = envinds[start:end]
                mb_inds = flatinds[:, mbenvinds].ravel()

                _, newlogprob, entropy, newvalue, _ = self.model.get_action_and_value(
                    obs[mb_inds],
                    initial_gru_state[:, mbenvinds],
                    dones[mb_inds],
                    actions.long()[mb_inds],
                )

                ratio = (newlogprob - logprobs[mb_inds]).exp()

                mb_advantages = advantages[mb_inds]

                self.optimizer.zero_grad()

                # Policy loss
                (
                    torch.max(
                        -mb_advantages * ratio,
                        -mb_advantages
                        * torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon),
                    ).mean()
                    - self.entropy_coef * entropy.mean()
                ).backward()

                # Value loss
                ((newvalue.view(-1) - returns[mb_inds]) ** 2).mean().backward()

                nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                self.optimizer.step()

        torch.save(self.model.state_dict(), self.savepath)
        return next_gru_state, next_state, next_done

    def test_step(self, next_gru_state, next_state, next_done):
        with torch.no_grad():
            action, next_gru_state = self.model.predict_action(
                next_state, next_gru_state, next_done
            )
            next_state, reward, done = self.envs.step(action.cpu().numpy())
            next_state = torch.Tensor(next_state).to(self.device)
            next_done = torch.Tensor(done).to(self.device)
        return next_gru_state, next_state, reward, next_done

    def run(self, train_mode=1):
        next_state = torch.Tensor(self.envs.reset()).to(self.device)
        next_done = torch.zeros(self.num_envs).to(self.device)
        if train_mode == 1:
            self.model.train()
            next_gru_state = torch.zeros(2, self.num_envs, 256).to(self.device)
            while True:
                next_gru_state, next_state, next_done = self.sample_update(
                    next_gru_state, next_state, next_done
                )
        else:
            self.model.eval()
            if self.num_envs == 1:
                test_reward = 0
                test_episode_num = 0
                test_reward_list = []
            next_gru_state = torch.zeros(self.num_envs, 256).to(self.device)
            while True:
                next_gru_state, next_state, reward, next_done = self.test_step(
                    next_gru_state, next_state, next_done
                )
                if self.num_envs == 1 and next_done:
                    if test_reward != 0:
                        if self.test_Mode == "TSR":
                            with open("../../Webots_Simulation/traffic_project/config/env_config.json", "r") as file:
                                data = json.load(file)
                            total_step = data["Train_Total_Steps"]
                            freq = data["Control_Frequence"]
                            TSR =  test_reward / total_step * (500/freq)
                            test_reward_list.append(TSR)
                            print(f"episode: {test_episode_num} tracking success rate: {TSR}")
                        elif self.test_Mode == "CR":
                            test_reward_list.append(test_reward)
                            print(f"episode: {test_episode_num} test_reward: {test_reward}")
                        test_episode_num += 1
                        
                    if len(test_reward_list) == 10:
                        test_reward_list.append(
                            f"{np.mean(test_reward_list):.3f}±{np.std(test_reward_list):.3f}"
                        )
                        import pandas as pd

                        df = pd.DataFrame(test_reward_list, columns=["Values"])
                        df.to_excel(f"./models/R_VAT/RVAT_logs/RVAT_test.xlsx", index=False)
                    test_reward = 0
                else:
                    test_reward += float(reward[0])

if __name__ == "__main__":
    import argparse

    # --------------------------------------------------parameter-----------------------------------------------
    parse = argparse.ArgumentParser(description="run RPPO")
    parse.add_argument(
        "-w",
        "--workers",
        default=24,
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
        default="./models/R_VAT/params.pth",
        type=str,
        metavar="",
        help="model parameter filename, default: ./models/R_VAT/params.pth",
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
        help="the port of tensorboard, recommended: 6006. Default is -1 (TensorBoard disabled). Set to any other value to enable TensorBoard, which will find an available port if needed.",
    )
    parse.add_argument(
        "-N",
        "--New_Train",
        action="store_true",
        default=False,
        help="whether restart a new training, default: False",
    )
    parse.add_argument(
        "-ver",
        "--verbose",
        action='store_true',
        default=False,
        help="Whether need verbose",
    )
    parse.add_argument(
        "-D",
        "--delay",
        type=int,
        default=20,
        help="Delay after webots start",
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
    data["Verbose"] = args.verbose
    if args.train_mode == 1:
        data["Drone_Random_Config"]["height_random"] = True
        data["Drone_Random_Config"]["view_pitch_random"] = True
        data["Drone_Random_Config"]["direction_random"] = True
        data["Drone_Random_Config"]["horizon_bias_random"] = True
        data["Drone_Random_Config"]["verticle_bias_random"] = True
        data["Sumo_Params"]["fixed_seed"] = False
        data["Sumo_Params"]["fixed_car_group_num"] = False
        data["Reward_Config"]["reward_mode"] = "continuous"
        data["Reward_Config"]["view_range"] = 0.7
        data["No_Reward_Done_Steps"] = 100
    else:
        data["Drone_Random_Config"]["height_random"] = False
        data["Drone_Random_Config"]["view_pitch_random"] = False
        data["Drone_Random_Config"]["direction_random"] = False
        data["Drone_Random_Config"]["horizon_bias_random"] = False
        data["Drone_Random_Config"]["horizon_bias_fixed"] = 0
        data["Drone_Random_Config"]["verticle_bias_random"] = False
        data["Drone_Random_Config"]["verticle_bias_fixed"] = 0
        data["Sumo_Params"]["fixed_color"] = False
        data["Sumo_Params"]["fixed_seed"] = True
        data["Sumo_Params"]["fixed_car_group_num"] = True
        data["No_Reward_Done_Steps"] = 10000
        if args.Test_Mode == "CR":
            data["Reward_Config"]["reward_mode"] = "continuous"
            data["Reward_Config"]["view_range"] = 1
        elif args.Test_Mode == "TSR":
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
    data["Benchmark"]["RewardType"] = "default"

    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

    if args.New_Train and os.path.exists("./models/R_VAT/RVAT_logs/steps.txt"):
        with open("./models/R_VAT/RVAT_logs/steps.txt", "w") as file:
            file.write("0")

    if args.train_mode == 1:
        Load_Model = not args.New_Train
    else:
        Load_Model = True

    import subprocess, time

    # simulator
    simulator = subprocess.Popen(
        ["webots ../../Webots_Simulation/traffic_project/worlds/" + args.map],
        shell=True,
    )
    time.sleep(args.delay)

    from envs.envs_parallel import Envs, GE

    agent = RVAT(
        envs=Envs(
            num_envs=args.workers,
            env_list=GE(args.workers, data["Benchmark"]),
            logs_show=(0 if args.tensorboard_port == -1 else args.workers),
        ),
        num_envs=args.workers,
        num_minibatches=1,
        num_steps=50,
        K_epochs=5,
        entropy_coef=0.01,
        gamma=0.9,
        savepath=args.savepath,
        load=Load_Model,
        test_Mode = args.Test_Mode
    )

    if args.tensorboard_port != -1 and args.train_mode == 1:
        tb = subprocess.Popen(
            ["tensorboard --logdir ./models/R_VAT/RVAT_logs"],
            shell=True,
        )

    with open("config.json", "r") as file:
        data = json.load(file)
    data["Benchmark"]["auto_start"] = False
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)

    agent.run(train_mode=args.train_mode)

