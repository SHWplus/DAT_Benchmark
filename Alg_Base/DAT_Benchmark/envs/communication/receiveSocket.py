import socket
import os
import numpy as np
import cv2
import time
from copy import deepcopy
import math

def is_file_in_use(file_path):
    try:
        os.rename(file_path, file_path)
    except OSError:
        return True
    else:
        return False

"""
    RecvRewardDoneSocketPort
        1. The class use for receiving reward/done/current step/other state
        2. Can support 2 modes: Socket mode & File mode(recommand)
"""
class RecvRewardDoneSocketPort:
    """
        __init__:Initialize RecvRewardDoneSocketPort
            1. Initialize all receive data
            2. Initialize reward file path(mode)
        Input:
            _data_size(Int): total data size for reward+done+curr_step+other_state
            id(Int): Port use for udp socket in socket mode
            reward_path(Str): Reward file path
        Output:
            None
    """
    def __init__(self, _data_size, id=7798,reward_path = None):
        ## Init udp socket
        if reward_path is None:
            self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp_socket.bind(('',id))

        self.data_size = int(_data_size)
        
        ## Init the receive data
        self.s = b''
        self.slist = []
        self.data = [0] * self.data_size
        self.data_last = [0] * self.data_size
        self.sdata = ["0"] * self.data_size

        ## Init reward file path(if == None:Socket mode)
        self.reward_path = reward_path

    '''
        read:
            read reward/done/current step/other state for Socket/File mode
            1. If in socket mode,read reward from udp socket and decode
            2. If in file mode,obey the following steps:
                Step1: If reward file not exists, wait
                Step2: If reward file is empty, delete file and return last reward
                Step3: Read reward from file and decode
                Step4: Update last reward and delete reward file  
        Input:
            Void
        Output:
            Reward: Reward
            Done: Done
            Curr_step: Current Step
            Other_state: Supple State
    '''    
    def read(self,imgPath):
        if self.reward_path is None:
            self.s,_=self.udp_socket.recvfrom(1024)
            if self.s != b'':
                self.slist = self.s.decode('utf-8').rstrip().split(',')
                if self.data_size>1:
                    self.is_rec = (self.slist[0] != '' and self.slist[1] != '')
                else:
                    self.is_rec = self.slist[0] != ''
                if self.is_rec:
                    self.is_rec = False 
                    for i in range(self.data_size):
                        self.data[i] = float(self.slist[i])
                        self.sdata[i] = self.slist[i]
        else:
            while not os.path.exists(self.reward_path):
                # if os.path.exists(imgPath):
                #     os.unlink(imgPath)
                time.sleep(0.001)
            while os.path.getsize(self.reward_path) == 0:
                time.sleep(0.001)
                while is_file_in_use(self.reward_path):
                    pass
                # os.unlink(self.reward_path)
                # return self.data_last[-2],self.data_last[-1], self.data_last[0],self.data_last[1:-2]
            with open(self.reward_path,'rb') as file:
                self.s = file.read()
                file.close()
            if self.s != b'':
                self.slist = self.s.decode('utf-8').rstrip().split(',')
                if self.data_size>1:
                    self.is_rec = (self.slist[0] != '' and self.slist[1] != '')
                else:
                    self.is_rec = self.slist[0] != ''
                if self.is_rec:
                    self.is_rec = False 
                    for i in range(self.data_size):
                        self.data[i] = float(self.slist[i])
                        self.sdata[i] = self.slist[i]
        self.data_last = deepcopy(self.data)
        while is_file_in_use(self.reward_path):
            pass
        while os.path.exists(self.reward_path):
            os.unlink(self.reward_path)
        return self.data[-2],self.data[-1], self.data[0],self.data[1:-2]

"""
    RecvImgSocketPort
        1. The class use for receiving image
        2. Can support 2 modes: Socket mode & File mode(recommand)
"""
class RecvImgSocketPort:
    """
        __init__:Initialize RecvImgSocketPort
            1. Initialize all receive data
            2. Initialize image file path(mode)
        Input:
            _data_size(Int): total data size for image
            id(Int): Port use for udp socket in socket mode
            img_path(Str): Image file path
        Output:
            None
    """
    def __init__(self, _data_size, id=7780,img_path = None):
        ## Init udp socket
        if img_path is None:
            self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('',id))
        
        ## Init the receive data
        self.data_size = int(_data_size)
        self.s = b''
        self.slist = []
        self.data = [0] * self.data_size
        self.sdata = ["0"] * self.data_size

        ## Init image file path(if == None:Socket mode)
        self.img_path = img_path
        self.img_last = None
        
    """
        receive: Receive Image in Socket/File mode
            1. If in socket mode,read image from udp socket and decode
            2. If in file mode,obey the following steps:
                Step1: If image file not exists, wait
                Step2: If image file is empty, delete file and return last image
                Step3: Read image from file and decode
                Step4: Update last image and delete image file
                Step5: Re-detecting the existence of image file
        Input:
            reward_path: path of reward file
            reset: whether in reset function or not
            first_reset: whether the first time to reset
        Output:
            Img(np.ndarray)
    """
    def receive(self,reward_path,reset=False,first_reset=False):
        while os.path.exists(reward_path):
            while is_file_in_use(reward_path):
                pass
            os.unlink(reward_path)
            time.sleep(0.01)
        if self.img_path is None:
            data, _ = self.udp_socket.recvfrom(102400)
            if self.s != b'':
                self.slist = self.s.decode('utf-8').rstrip().split(',')
                if self.slist[0] != '' and self.slist[1] != '':
                    for i in range(self.data_size):
                        self.data[i] = float(self.slist[i])
                        self.sdata[i] = self.slist[i]
            nparr = np.fromstring(data, np.uint8)
            img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img_decode
        else:
            resetCount = 0
            while not os.path.exists(self.img_path):
                if not first_reset:
                    if reset:
                        resetCount = resetCount + 1
                        if resetCount > 500:
                            return np.array([1])
                time.sleep(0.001)
            while os.path.getsize(self.img_path) == 0:
                time.sleep(0.001)
                while is_file_in_use(self.img_path):
                    pass
                os.unlink(self.img_path)
                if self.img_last is not None:
                    return self.img_last
                else:
                    return np.zeros((320,240,3),np.uint8)
            imageRead = cv2.imread(self.img_path)
            self.img_last = deepcopy(imageRead)
            while os.path.exists(self.img_path):
                time.sleep(0.001)
                while is_file_in_use(self.img_path):
                    pass
                os.unlink(self.img_path)
            return imageRead

"""
    RecvStateMachineSocketPort(Not yet used in current)
        1. The class use for receiving State Machine
        2. Can Only support 1 mode: Socket mode
"""
class RecvStateMachineSocketPort:
    """
        __init__:Initialize RecvStateMachineSocketPort
            1. Initialize receive data
        Input:
            _data_size(Int): total data size for state machine
            id(Int): Port use for udp socket in socket mode
        Output:
            None
    """
    def __init__(self, _data_size=1, id=None):
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('',id))
        
        self.data_size = int(_data_size)
        
        ## Init the receive data
        self.s = b''
        self.slist = []
        self.data = [0] * self.data_size
        self.sdata = ["0"] * self.data_size
    
    """
        read: Receive State Machine in Socket mode
            1. If in socket mode,read State Machine from udp socket and decode
        Input:
            Void
        Output:
            None
    """
    def read(self):
        self.s,_=self.udp_socket.recvfrom(1024)
        if self.s != b'':
            self.slist = self.s.decode('utf-8').rstrip().split(',')
            if self.data_size>1:
                self.is_rec = (self.slist[0] != '' and self.slist[1] != '')
            else:
                self.is_rec = self.slist[0] != ''
            if self.is_rec:
                self.is_rec = False 
                for i in range(self.data_size):
                    self.data[i] = float(self.slist[i])
                    self.sdata[i] = self.slist[i]
        return self.data[0]

"""
    RecvPointCloud:Receive PointCloud in Socket/File mode
        1. The class use for receiving pointcloud
        2. Can support 2 modes: Socket mode & File mode(recommand)
"""
class RecvPointCloud:
    """
        __init__:Initialize RecvPointCloud
            1. Initialize all receive data
            2. Initialize point cloud file path(mode)
        Input:
            _data_size(Int): total data size for point cloud(default=2000)
            id(Int): Port use for udp socket in socket mode
            pointcloud_path_path(Str): Point Cloud file path
        Output:
            None
        Note:
            Since the length of Point Cloud tends not to be fixed,
            the actual length will be len(self.slist)
    """
    def __init__(self, _data_size=2000, id=None,pointcloud_path=None):
        ## Init udp socket
        if pointcloud_path is None:
            self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('',id))
        
        ## Init the receive data
        self.data_size = int(_data_size)
        self.s = b''
        self.slist = []
        self.data = [math.nan] * self.data_size
        self.data_last = [math.nan] * self.data_size

        ## Init pointcloud file path(if == None:Socket mode)
        self.pointcloud_path = pointcloud_path

    """
        read:
            read point cloud for Socket/File mode
            1. If in socket mode,read point cloud from udp socket and decode
            2. If in file mode,obey the following steps:
                Step1: If point cloud file not exists, wait
                Step2: If point cloud file is empty, delete file and return last point cloud
                Step3: Read point cloud from file and decode
                Step4: Update last point cloud and delete point cloud file
        Input:
            Void
        Output:
            Point Cloud
    """
    def read(self):
        if self.pointcloud_path is None:
            self.s,_=self.udp_socket.recvfrom(10240)
        else:
            while not os.path.exists(self.pointcloud_path):
                time.sleep(0.001)
            while os.path.getsize(self.pointcloud_path) == 0:
                time.sleep(0.001)
                while is_file_in_use(self.pointcloud_path):
                    pass
                # os.unlink(self.pointcloud_path)
                # return self.data_last
            with open(self.pointcloud_path,'rb') as file:
                self.s = file.read()
                file.close()
        if self.s != b'':
            self.slist = self.s.decode('utf-8').rstrip().split(',')
            self.data_size = len(self.slist)
            self.data = [math.nan] * self.data_size
            if self.data_size>1:
                self.is_rec = (self.slist[0] != '' and self.slist[1] != '')
            else:
                self.is_rec = self.slist[0] != ''
            if self.is_rec:
                self.is_rec = False 
                for i in range(self.data_size):
                    try:
                        self.data[i] = float(self.slist[i])
                    except ValueError:
                        self.data[i] = math.nan
                    except IndexError:
                        break
        self.data_last = deepcopy(self.data)
        while is_file_in_use(self.pointcloud_path):
            pass
        os.unlink(self.pointcloud_path)
        return self.data

"""
    RecvRewardParams:Receive Reward Params in Socket/File mode
        1. The class use for receiving Reward Params
        2. Can support 2 modes: Socket mode & File mode(recommand)
"""
class RecvRewardParams:
    """
        __init__:Initialize RecvRewardParams
            1. Initialize all receive data
            2. Initialize Reward Params file path(mode)
        Input:
            _data_size(Int): total data size for reward params(default=57)
            id(Int): Port use for udp socket in socket mode
            rewardparam_path_path(Str): Reward Params file path
        Output:
            None
    """
    def __init__(self, _data_size=61, id=None,rewardparam_path=None):
        ## Init udp socket
        if rewardparam_path is None:
            self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('',id))
        
        ## Init the receive data
        self.data_size = int(_data_size)
        self.s = b''
        self.slist = []
        self.data = [0] * (self.data_size-1)+["0"]
        self.sdata = ["0"] * self.data_size
        self.data_last = [0] * self.data_size

        ## Init rewardparam file path(if == None:Socket mode)
        self.rewardparam_path = rewardparam_path

    """
        read:
            read reward params for Socket/File mode
            1. If in socket mode,read reward params from udp socket and decode
            2. If in file mode,obey the following steps:
                Step1: If reward params file not exists, wait
                Step2: If reward params file is empty, delete file and return last reward params
                Step3: Read reward params from file and decode
                Step4: Update last reward params and delete reward params file  
        Input:
            Void
        Output:
            Reward Params
    """
    def read(self):
        if self.rewardparam_path is None:
            self.s,_=self.udp_socket.recvfrom(1024)
        else:
            while not os.path.exists(self.rewardparam_path):
                time.sleep(0.001)
            while os.path.getsize(self.rewardparam_path) == 0:
                time.sleep(0.001)
                while is_file_in_use(self.rewardparam_path):
                    pass
                # os.unlink(self.rewardparam_path)
                # return self.data_last
            with open(self.rewardparam_path,'rb') as file:
                self.s = file.read()
                file.close()
        if self.s != b'':
            self.slist = self.s.decode('utf-8').rstrip().split(',')
            if self.data_size>1:
                self.is_rec = (self.slist[0] != '' and self.slist[1] != '')
            else:
                self.is_rec = self.slist[0] != ''
            if self.is_rec:
                self.is_rec = False 
                for i in range(self.data_size):
                    if i != self.data_size-1:
                        self.data[i] = float(self.slist[i])
                    else:
                        self.data[i] = self.slist[i]
                    self.sdata[i] = self.slist[i]
        self.data_last = deepcopy(self.data)
        while is_file_in_use(self.rewardparam_path):
            pass
        os.unlink(self.rewardparam_path)
        return self.data