from __future__ import division
import numpy as np
import torch
import json
import logging
import math
import psutil
import os
import warnings
import time
import signal

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


def read_config(file_path):
    """Read JSON config."""
    json_object = json.load(open(file_path, 'r'))
    return json_object


def norm_col_init(weights, std=1.0):
    x = torch.randn(weights.size())
    x *= std / torch.sqrt((x**2).sum(1, keepdim=True))
    return x


def ensure_shared_grads(model, shared_model, gpu=False):
    for param, shared_param in zip(model.parameters(),
                                   shared_model.parameters()):
        if shared_param.grad is not None and not gpu:
            return
        elif not gpu:
            shared_param._grad = param.grad
        else:
            shared_param._grad = param.grad.cpu()


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        weight_shape = list(m.weight.data.size())
        fan_in = np.prod(weight_shape[1:4])
        fan_out = np.prod(weight_shape[2:4]) * weight_shape[0]
        w_bound = np.sqrt(6. / (fan_in + fan_out))
        m.weight.data.uniform_(-w_bound, w_bound)
        m.bias.data.fill_(0)
    elif classname.find('Linear') != -1:
        weight_shape = list(m.weight.data.size())
        fan_in = weight_shape[1]
        fan_out = weight_shape[0]
        w_bound = np.sqrt(6. / (fan_in + fan_out))
        m.weight.data.uniform_(-w_bound, w_bound)
        m.bias.data.fill_(0)

def clip_to_range(x, min_value=0, max_value=1):
    return max(min_value, min(x, max_value))

"""
    reward of baseline method: End-to-end
        reward = A - (sqrt((x-d)^2+y^2)/c+lambda|w-w_0|)
"""
def get_E2E_reward(x:float,y:float,w:float,d_curr:float,Fov:float)->float:
    A = 1
    c = 9
    lamb = 2/Fov
    ## get reward
    dist = math.sqrt(math.pow(x-d_curr,2)+math.pow(y,2))/c
    w_abs = lamb*abs(w)
    reward = A-(dist+w_abs)
    reward = clip_to_range(reward,min_value=-1,max_value=1)
    return reward,dist,w_abs

"""
    reward of baseline method: DVAT
        reward = re-k_v*rv-ku*ru
"""
def get_DVAT_reward(A_fov:float,d_cmd:float,x:float,y:float,z:float,v:list,u:list,crash:bool,discrete=True):
    ## Hyperparams
    beta = 1/3
    # k_v = 0.4
    k_v = 0
    k_u = 0.4
    k_c = 10
    if crash:
        return -k_c,None,None
    else:
        ## get reward
        rx = max(0,1-abs(x-d_cmd))
        ry = max(0,1-abs(2/A_fov*math.atan(y/x)))
        if discrete:
            rz = 1
        else:
            rz = max(0,1-abs(2/A_fov*math.atan(z/x)))

        re = clip_to_range(math.pow(rx*ry*rz,beta))

        v_norm = math.sqrt(math.pow(v[0],2)+math.pow(v[1],2)+math.pow(v[2],2))
        rv = v_norm/(1+v_norm)
        u_norm = math.sqrt(math.pow(u[0],2)+math.pow(u[1],2)+math.pow(u[2],2))
        ru = u_norm/(1+u_norm)
        reward = re-k_v*rv-k_u*ru
        return reward,rx,ry

def check_memory_usage(target_pid:int,threshold:float=0.85)->float:
    while True:
        memory_info = psutil.virtual_memory()

        # Get memory comsumption in percentage
        memory_usage = memory_info.percent

        if memory_usage > 60:
            warnings.warn("---- Memory allocation over 60% ---- ")

        if memory_usage > threshold*100:
            warnings.warn(f"---- Memory allocation over {threshold*100}% ---- ")
            os.kill(target_pid, signal.SIGKILL)
        
        time.sleep(5)

def judge_vel_eff(vel:list,thresholdx:float=50.0,thresholdy:float=50.0,maxx:float=40.0,maxy:float=40.0)->list:
    vel_norm = [0.0,0.0,0.0]
    if abs(vel[0])>=thresholdx:
        vel_norm[0] = sign(vel[0])*maxx
    else:
        vel_norm[0] = vel[0]
    if abs(vel[1])>=thresholdy:
        vel_norm[1] = sign(vel[1])*maxy
    else:
        vel_norm[1] = vel[1]
    vel_norm[2] = vel[2]
    return vel_norm

def sign(num:float):
    if num >= 0:
        return 1
    else:
        return -1

def get_mean_std(reward_list:list):
    mean = np.mean(reward_list)
    std = np.std(reward_list)
    return mean,std

if __name__ == "__main__":
    mean,std = get_mean_std([8.178,0.01322,0.008,2.563,0.5019])
    print(f"mean: {mean} std: {std}")