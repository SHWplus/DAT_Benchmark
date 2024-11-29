from __future__ import division
import os
os.environ["OMP_NUM_THREADS"] = "1"
import torch
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
import random

class Agent(object):
    def __init__(self, model, env, args, state,process_func):
        self.model = model
        self.env = env
        self.state = state
        self.suppleinfo = []
        self.privilegeinfo = None
        self.hx = None
        self.cx = None
        self.eps_len = 0
        self.args = args
        self.values = []
        self.log_probs = []
        self.rewards = []
        self.entropies = []
        self.done = True
        self.info = None
        self.reward = 0
        self.gpu_id = -1
        self.hidden_size = args.hidden_size
        self.process_func = process_func
        self.epsilon = args.epsilon

    def action_train(self):
        if self.args.train_mode == "privilege":
            if self.info == None:
                pass
            else:
                self.privilegeinfo = self.int2one_hot(int(self.info[0][-1]),self.args.previlege_dim)
            
        value, logit, self.hx, self.cx = self.model(
            self.state.unsqueeze(0), self.hx, self.cx,self.privilegeinfo
        )
        prob = F.softmax(logit, dim=1)
        log_prob = F.log_softmax(logit, dim=1)
        entropy = -(log_prob * prob).sum(1)
        self.entropies.append(entropy)
        action = prob.multinomial(1).data
        ## epsilon greedy
        ran = random.random()
        if ran < self.epsilon:
            pass
        else:
            rand_action = random.randint(0,6)
            action = torch.tensor([[rand_action]])
        log_prob = log_prob.gather(1, action)
        state, self.reward, self.done, self.info = self.env.step(action.item(),prob)
        
        state = self.process_func(state = state,env=self.env)
        if self.gpu_id >= 0:
            with torch.cuda.device(self.gpu_id):
                self.state = torch.from_numpy(state).float().cuda()
        else:
            self.state = torch.from_numpy(state).float()
        self.eps_len += 1
        
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.rewards.append(self.reward)
        return self

    def action_test(self):
        with torch.no_grad():
            if self.done:
                if self.gpu_id >= 0:
                    with torch.cuda.device(self.gpu_id):
                        self.cx = torch.zeros(1, self.hidden_size).cuda()
                        self.hx = torch.zeros(1, self.hidden_size).cuda()
                else:
                    self.cx = torch.zeros(1, self.hidden_size)
                    self.hx = torch.zeros(1, self.hidden_size)

            value, logit, self.hx, self.cx = self.model(
                self.state.unsqueeze(0), self.hx, self.cx,self.privilegeinfo
            )
            prob = F.softmax(logit, dim=1)
            action = prob.cpu().numpy().argmax()
        state, self.reward, self.done, self.info = self.env.step(action)
        if self.args.train_mode == "privilege":
            self.privilegeinfo = self.int2one_hot(int(self.info[0][-1]),self.args.previlege_dim)
        state = self.process_func(env=self.env,state = state)
        if self.gpu_id >= 0:
            with torch.cuda.device(self.gpu_id):
                self.state = torch.from_numpy(state).float().cuda()
        else:
            self.state = torch.from_numpy(state).float()

        self.eps_len += 1
        return self

    def clear_actions(self):
        self.values = []
        self.log_probs = []
        self.rewards = []
        self.entropies = []
        return self

    def int2one_hot(self,idx:int,num_class:int)->torch.Tensor:
        zero_arr = np.zeros((num_class))
        zero_arr[idx] = 1 # idx range from 0 to num_class-1
        zero_tensor = torch.Tensor(zero_arr)
        zero_tensor = torch.unsqueeze(zero_tensor,0)
        return zero_tensor