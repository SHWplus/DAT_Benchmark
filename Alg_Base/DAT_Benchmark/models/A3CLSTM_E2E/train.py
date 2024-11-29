from __future__ import division
import os
os.environ["OMP_NUM_THREADS"] = "1"
from setproctitle import setproctitle as ptitle
import torch
import torch.optim as optim
from envs.environment import general_env
from utils import ensure_shared_grads
from model import A3Clstm,A3ClstmE2E
from player_util import Agent
from torch.autograd import Variable
import time
import logging
from logs.Empty_Log import Empty_Logger


def train(rank, args, shared_model, optimizer, env_conf,log = False):
    if log:
        logger = logging.getLogger(f'train_logger_{rank}')
        logger.setLevel(logging.INFO)
        if os.path.exists(f"./logs/Agent_train{rank}.log"):
            os.unlink(f"./logs/Agent_train{rank}.log")
        file_handler = logging.FileHandler(f"./logs/Agent_train{rank}.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(file_handler)
    else:
        logger = Empty_Logger()

    episode = 0
    ptitle(f"Train Agent: {rank}")
    gpu_id = args.gpu_ids[rank % len(args.gpu_ids)]
    torch.manual_seed(args.seed + rank)
    if gpu_id >= 0:
        torch.cuda.manual_seed(args.seed + rank)
    hidden_size = args.hidden_size
    env,process_func = general_env(args.env, env_conf,args.workers,process_idx=rank)
    if optimizer is None:
        if args.optimizer == 'RMSprop':
            optimizer = optim.RMSprop(shared_model.parameters(), lr=args.lr)
        if args.optimizer == 'Adam':
            optimizer = optim.Adam(
                shared_model.parameters(), lr=args.lr, amsgrad=args.amsgrad)
    player = Agent(None, env, args, None,process_func)
    player.gpu_id = gpu_id
    if args.model_type == "Default":
        player.model = A3Clstm(env_conf["State_channel"], env_conf["Action_dim"], args)
    elif args.model_type == "E2E":
        player.model = A3ClstmE2E(env_conf["State_channel"], env_conf["Action_dim"], args)

    player.state,player.suppleinfo = player.env.reset()
    if args.train_mode == "privilege":
        player.privilegeinfo = player.int2one_hot(int(player.suppleinfo[0][-1]),args.previlege_dim)
    player.state = process_func(state = player.state,env=player.env)
    if gpu_id >= 0:
        with torch.cuda.device(gpu_id):
            player.state = torch.from_numpy(player.state).float().cuda()
            player.model = player.model.cuda()
    else:
        player.state = torch.from_numpy(player.state).float()
    player.model.train()
    if len(args.distributed_step_size) > 0:
        num_steps = args.distributed_step_size[rank%len(args.distributed_step_size)]
    else:
        num_steps = args.num_steps
    try:
        while episode < args.max_episode_length:
            logger.info("\n")
            if gpu_id >= 0:
                with torch.cuda.device(gpu_id):
                    player.model.load_state_dict(shared_model.state_dict())
            else:
                player.model.load_state_dict(shared_model.state_dict())
            if player.done:
                if gpu_id >= 0:
                    with torch.cuda.device(gpu_id):
                        player.cx = torch.zeros(1, hidden_size).cuda()
                        player.hx = torch.zeros(1, hidden_size).cuda()
                else:
                    player.cx = torch.zeros(1, hidden_size)
                    player.hx = torch.zeros(1, hidden_size)
            else:
                player.cx = player.cx.data
                player.hx = player.hx.data

            
            for step in range(num_steps):
                player.action_train()
                if player.done:
                    break
            if player.done:
                player.eps_len = 0
                state,player.suppleinfo = player.env.reset()
                if args.train_mode == "privilege":
                    player.privilegeinfo = player.int2one_hot(int(player.suppleinfo[0][-1]),args.previlege_dim)
                    player.info = None
                state = process_func(state = state,env=player.env)
                if gpu_id >= 0:
                    with torch.cuda.device(gpu_id):
                        player.state = torch.from_numpy(state).float().cuda()
                else:
                    player.state = torch.from_numpy(state).float()

            if gpu_id >= 0:
                with torch.cuda.device(gpu_id):
                    R = torch.zeros(1, 1).cuda()
                    gae = torch.zeros(1, 1).cuda()
            else:
                R = torch.zeros(1, 1)
                gae = torch.zeros(1, 1)
            if not player.done:
                state = player.state
                value, _, _, _ = player.model(
                    state.unsqueeze(0), player.hx, player.cx,player.privilegeinfo
                )
                
                R = value.detach()
            player.values.append(R)
            policy_loss = 0
            value_loss = 0
            logger.info(f"episode_num: {episode}, player.rewards list: {player.rewards}")
            logger.info(f"episode_num: {episode}, player.values list: {player.values}")
            for i in reversed(range(len(player.rewards))):
                R = args.gamma * R + player.rewards[i]
                logger.info(f"iter_num: {i}, R: {R}")
                advantage = R - player.values[i]
                logger.info(f"iter_num: {i}, advantage: {advantage}")
                value_loss = value_loss + 0.5 * advantage.pow(2)
                logger.info(f"iter_num: {i}, delta value_loss: {0.5 * advantage.pow(2)}")
                
                # Generalized Advantage Estimataion
                delta_t = (
                    player.rewards[i]
                    + args.gamma * player.values[i + 1].data
                    - player.values[i].data
                )

                gae = gae * args.gamma * args.tau + delta_t
                policy_loss = (
                    policy_loss
                    - (player.log_probs[i] * gae)
                    - (args.entropy_coef * player.entropies[i])
                )

                logger.info(f"\n")
            logger.info(f"episode_num: {episode}, value_loss: {value_loss}")
            logger.info(f"episode_num: {episode}, delta_t: {delta_t}")
            logger.info(f"episode_num: {episode}, policy_loss: {policy_loss}")
            logger.info(f"\n")

            player.model.zero_grad()
            (policy_loss + 0.5 * value_loss).backward()
            
            ensure_shared_grads(player.model, shared_model, gpu=gpu_id >= 0)
            optimizer.step()
            player.clear_actions()
            if episode % 10 == 0 and episode != 0:
                torch.save(player.model.state_dict(), args.save_model_dir+args.model_type+str(episode)+'.pth')
    except KeyboardInterrupt:
        time.sleep(0.01)
        print("KeyboardInterrupt exception is caught")
    finally:
        print(f"train agent {rank} process finished")
