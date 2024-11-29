import socket
import queue
import threading
from multiprocessing import Process
import os
import cv2
import numpy as np
import shutil
import time
from copy import deepcopy
import logging

def is_file_in_use(file_path):
    try:
        os.rename(file_path, file_path)
    except OSError:
        return True
    else:
        return False

'''
description: set up a logger for debug
param {*} logger_name
param {*} log_file
param {*} level
return {*}
'''
def setup_logger(logger_name, log_file, level=logging.INFO):
    if os.path.exists(log_file):
        # with open(log_file,"r") as f:
        #     f.close()
        while is_file_in_use(log_file):
            pass
        os.unlink(log_file)
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

BASE_PORT = 6000

class MultiProcessRecv():
    Number_process = 0
    
    def __init__(self,trackerDef:str,tar_ip,max_data_size:int,ctrl_freq:float,process_port=7787,verbose=False) -> None:
        
        self.trackerDef = trackerDef
        self.tar_ip = tar_ip
        self.ctrl_freq = ctrl_freq
        base_dir = "../../Files2Alg/"
        
        # command = 'ifconfig enp108s0 192.168.1.1 netmask 255.255.255.0'
        # sudo_password = '1210'
        # sudo_command = f'echo {sudo_password} | sudo -S {command}'
        # os.system(sudo_command)
        
        self.socketPort = []
        self.udp_socket = None
        
        self.max_data_size = max_data_size
        self.process_port = process_port
        self.verbose = verbose
        MultiProcessRecv.Number_process = self.get_NumProcess(base_dir+"start.txt",process_port)
        self.s = [b'']*MultiProcessRecv.Number_process
        self.s_last = [b'']*MultiProcessRecv.Number_process
        self.data = [[0]*self.max_data_size]*MultiProcessRecv.Number_process
        self.slist = [['']]*MultiProcessRecv.Number_process
        
        self.actionSize = 5
        self.is_step = [0]*MultiProcessRecv.Number_process # Whether Trigger a step
        self.is_reset = [False]*MultiProcessRecv.Number_process # Whether Trigger a reset
        
        # create logger list
        self.logger_list = []
        
        self.ProcessSocket_list = []
        self.queuelist = []
        self.rgetqueue = [[0]*self.max_data_size]*MultiProcessRecv.Number_process
        self.Action_list = [[0]*self.max_data_size]*MultiProcessRecv.Number_process
        self.readAction_list = self.Action_list
        self.Create_Process()
        self.Receive_queue()
        
        self.actionCount = 0
        
        self.stateInit = False
        self.pointCloudInit = False
        self.makeRewardInit = False
        
        self.savedir = []
        
        for i in range(MultiProcessRecv.Number_process):
            id_path = base_dir+"recv_action"+str(i)+".txt"
            self.savedir.append(id_path)
    
        

    """
        get_NumProcess(port = 7787): Receive Number of Process set by client
        Input:
            Port: The port used to receive Number Process
        Output:
            Number_process: Number of Process
    """
    def get_NumProcess(self,filePath,Processport=7787):
        with open(filePath, "wb") as f:
                data = bytes(str(1) + "\n", 'utf-8')
                f.write(bytes(str(data) + "\n", 'utf-8'))
                f.close()
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_socket.bind(('',Processport))
        Numprocess_bytes = self.udp_socket.recvfrom(256)[0]
        Number_process = int(Numprocess_bytes)
        return Number_process

    """
        Create_Process: Allocate Port for Multi-Process
        Input:
            MultiProcessRecv.Number_process: Number of Process User want to use(Receive from get_NumProcess())
        Output:
            self.ProcessSocket_list: 2D List(Shape:[NumProcess,4]) contains 4 socket for corresponding port and for all Process
                Socket 1: Webots SsendImage(self, filepath, idx:int)end Image to Client
                Socket 2: Webots Send State Machine Flag to Client
                Socket 3: Webots Send Env State , Reward and Done to Client
                Socket 4: Client Send Action and ResetFlag to Webots
                Socket 5: Webots Send Radar Cloud Point Data to Client
                Socket 6: Webots Send Make Reward Data to Client
    """
    def Create_Process(self):
        print(MultiProcessRecv.Number_process)
        for i in range(MultiProcessRecv.Number_process):
            if self.verbose == True:
                setup_logger(self.trackerDef+str(i),"../../logs/Agent"+str(i)+".log")
                self.logger_list.append(logging.getLogger(self.trackerDef+str(i)))
            # Curr_Process = []
            # for port in range(6):
            #     self.socketPort.append(BASE_PORT + i*6 + port)
            #     udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            #     if port == 3:
            #         udp_socket.bind(('',self.socketPort[i*6 + port]))
            #     Curr_Process.append(udp_socket)
            # self.ProcessSocket_list.append(Curr_Process)

    """
        Receive_queue(self,NumProcess): Init the queue list for multi-process
        Input:
            MultiProcessRecv.Number_process: Number of Process get from get_NumProcess(port = 7787) Function
        Output:
            self.queuelist: A list of queue with size = NumProcess,Each queu/home/lu/Git_Project/github/webots_autodriving_drone/traffic_project_bridge/Files2Alg/e save action from corresponding process
    """
    def Receive_queue(self):
        for i in range(MultiProcessRecv.Number_process):
            self.queuelist.append(queue.Queue(maxsize=1))
            self.readAction_list.append(self.data[i])

    """
        Single_action: Sigle Recv Action function for each thread
            1. Decode the Action Data
            2. Push the Action Data into queue if empty
    """
    def Single_action(self,idx:int, action_path:str=None, cimg_path:str=None):
        epoch=0
        while True:
            epoch+=1
            if action_path is None:
                self.s[idx],_=self.ProcessSocket_list[idx][3].recvfrom(1024) # one receive
            else:
                if self.verbose == True:
                    self.logger_list[idx].info("trying receive action")
                while not os.path.exists(action_path):
                    time.sleep(0.001)
                while os.path.getsize(action_path) == 0:
                    time.sleep(0.001)
                    
                with open(action_path, "r") as f:
                    self.s[idx] = f.readline()
                    f.close()
                if self.verbose == True:
                    self.logger_list[idx].info("finish receive action:  "+self.s[idx])
                if self.verbose == True:
                    self.logger_list[idx].info("writing for the action to be deleted")
                if self.s[idx] != b'' and self.s[idx] != b'\n':
                    while os.path.exists(self.savedir[idx]):
                        time.sleep(0.001)
                        
                    if self.verbose == True:
                        self.logger_list[idx].info("writing action to:  "+str(self.savedir[idx]))
                    with open(self.savedir[idx],"w") as actionfile:
                        actionfile.write(self.s[idx])
                        # self.actionCount = 0
                        actionfile.close()
                    if self.verbose == True:
                        self.logger_list[idx].info("Finish writing action")
                    
            if action_path is not None:
                while is_file_in_use(action_path):
                    pass
                os.unlink(action_path)

    """if self.queuelist[idx].full()or corresponding process
    """
    def Recv_action(self):
        self.thread_list = []
        for i in range(MultiProcessRecv.Number_process):
            t = threading.Thread(target = self.Single_action,args=(i,
                                                                   "../../Files2Alg/" + self.trackerDef + str(i) + "_AlgAction.txt",
                                                                   "../../Files2Alg/" + self.trackerDef + str(i) + "_VideoFrame.txt"))
            self.thread_list.append(t)
        for j in range(MultiProcessRecv.Number_process):
            self.thread_list[j].start()

    """
        Get_flags(self): Judge if all the Queue are full,if so Pop all the Actio out and send a flag to Step
        Input:
            self.queuelist: A list of queue with size = NumProcess,Each queue save action from corresponding process
        Output:
            Action_list: List of Actions of Corresponding Process
    """
    def Get_flags(self):
        epoch = 0
        lastrgetqueue = [0.0,0.0,0.0,0.0,0.0]
        while True:
            epoch+=1
            get_flag = True
            for process in range(MultiProcessRecv.Number_process):
                while not os.path.exists(self.savedir[process]):
                    time.sleep(0.001)
                
            for getqueue in range(MultiProcessRecv.Number_process):
                with open(self.savedir[getqueue],'r') as queuefile:
                    action_get = queuefile.readline()
                    queuefile.close()
                if action_get == '':
                    rgetqueue = lastrgetqueue
                else:
                    # if self.verbose == True:
                    #     self.logger_list[getqueue].info("Action_get:  "+action_get)
                    rgetqueue = [float(x) for x in action_get.rstrip().split(',')]
                if self.verbose == True:
                    self.logger_list[getqueue].info("IDX:  "+str(getqueue)+"  real get actions: " + str(rgetqueue))
                self.Action_list[getqueue] = rgetqueue
                lastrgetqueue = rgetqueue
                self.is_step[getqueue] = self.is_step[getqueue] + int(1000./2./self.ctrl_freq)
                self.is_reset[getqueue] = self.Action_list[getqueue][4]
                if self.verbose == True:
                    self.logger_list[getqueue].info("Unlink the file: " + str(self.savedir[getqueue]))
                while is_file_in_use(self.savedir[getqueue]):
                    pass
                os.unlink(self.savedir[getqueue])
                
                self.readAction_list = deepcopy(self.Action_list)
                    
        
        
    """
        getAction(self, idx): get a action related to object idx
        Input:
            idx: object idx (int)
        Output:
            Action: Action of Corresponding Process (list)
    """
    def getAction(self, idx:int):
        return self.readAction_list[idx]
    
    """
        sendImage(self, filepath, idx:int): Webots Send Image to Client
        Input:
            filepath: the address that save the image
            idx: object idx (int) 
        Output:
            None
    """
    def sendImage(self, gfilePath, idx:int, sfilePath:str=None, cfilePath:str=None):
        if sfilePath is None:
            sendAddress = (self.tar_ip,self.socketPort[idx*6 + 0])
            image_size = [240,320,3]
            if os.path.exists(gfilePath):
                frame = cv2.imread(gfilePath)
                if frame is None:
                    frame = np.zeros(shape=image_size)
            else:
                frame = np.zeros(shape=image_size)
            img_encode = cv2.imencode('.jpeg', frame)[1]
            data_encode = np.array(img_encode)
            while data_encode[-1] != '\xd9' or data_encode[-2] != '\xff':
                if self.verbose == True:
                    self.logger_list[idx].info("get good graph")
                if os.path.exists(gfilePath):
                    frame = cv2.imread(gfilePath)
                if frame is None:
                    frame = np.zeros(shape=image_size)
                else:
                    frame = np.zeros(shape=image_size)
                img_encode = cv2.imencode('.jpeg', frame)[1]
                data_encode = np.array(img_encode)
                time.sleep(0.001)
            data = data_encode.tobytes()
            # send data:
            self.ProcessSocket_list[idx][0].sendto(data,sendAddress)
        else:
            while os.path.exists(sfilePath):
                time.sleep(0.001)
            
            tail_content = None
            while tail_content != b'\xff\xd9':
                if os.path.exists(gfilePath):
                    if os.path.getsize(gfilePath) != 0:
                        try:
                            with open(gfilePath, 'rb') as f:
                                f.seek(-2, 2)
                                tail_content = f.read()
                                # if self.verbose == True:
                                #     self.logger_list[idx].info("tail_content:    "+str(tail_content))
                                f.close()
                        except OSError:
                            print("os_error")
                time.sleep(0.001)
            
            shutil.copyfile(gfilePath, sfilePath)
            # os.system("cp -f " + gfilePath + " " + sfilePath)
            # with open(cfilePath,"w") as f:
            #     f.write(str(1))
            #     f.close()
            while os.path.exists(sfilePath):
                time.sleep(0.001)
            
        
    """
        sendState(self, stateStr:str, idx:int): Webots Send Env State , Reward and Done to Client
        Input:
            stateStr: the string to send
            idx: object idx (int) 
        Output:
            None
    """
    def sendState(self, stateStr:str, idx:int, filePath:str=None):
        if filePath is None:
            sendAddress = (self.tar_ip,self.socketPort[idx*6 + 2])
            data = bytes(stateStr, 'utf-8')
            self.ProcessSocket_list[idx][2].sendto(data,sendAddress)
        else:
            if self.stateInit == True:
                while os.path.exists(filePath):
                    time.sleep(0.001)
                with open(filePath, "wb") as f:
                    f.write(bytes(stateStr, 'utf-8'))
                    f.close()
                while os.path.exists(filePath):
                    try:
                        while os.path.getsize(filePath) < 1:
                            os.unlink(filePath)
                            time.sleep(0.001)
                            with open(filePath, "wb") as f:
                                f.write(bytes(stateStr, 'utf-8'))
                                f.close()
                            time.sleep(0.001)
                    except:
                        pass
                    time.sleep(0.001)
            else:
                with open(filePath, "wb") as f:
                    f.write(bytes(stateStr, 'utf-8'))
                    f.close()
                self.stateInit = True
    

    """
        sendMachine(self, state:float, idx:int): Webots Send State Machine Flag to Client
        Input:
            state: the machine state to send
            idx: object idx (int) 
        Output:
            None
    """   
    def sendMachine(self, state:float, idx:int, filePath:str=None):
        if filePath is None:
            sendAddress = (self.tar_ip,self.socketPort[idx*6 + 1])
            data = bytes(str(state) + "\n", 'utf-8')
            self.ProcessSocket_list[idx][1].sendto(data, sendAddress)
        else:
            with open(filePath, "wb") as f:
                f.write(bytes(str(state) + "\n", 'utf-8'))
                f.close()
                
    def keepSocketRunning(self):
        sendAddress = (self.tar_ip,self.process_port)
        data = bytes(str(0) + "\n", 'utf-8')
        self.udp_socket.sendto(data, sendAddress)
        
        
    """
        sendPointCloud(self, pointCloud:str, idx:int): Webots Send Radar Cloud Point Data to Client
        Input:
            pointCloud: the lidar point cloud to send
            idx: object idx (int) 
        Output:
            None
    """ 
    def sendPointCloud(self, pointCloud:str, idx:int, filePath:str=None):
        if filePath is None:
            sendAddress = (self.tar_ip,self.socketPort[idx*6 + 4])
            data = bytes(pointCloud, 'utf-8')
            self.ProcessSocket_list[idx][4].sendto(data,sendAddress)
        else:
            if self.pointCloudInit == True:
                while os.path.exists(filePath):
                    time.sleep(0.001)
                with open(filePath, "wb") as f:
                    f.write(bytes(pointCloud, 'utf-8'))
                    f.close()
                while os.path.exists(filePath):
                    try:
                        while os.path.getsize(filePath) < 1:
                            os.unlink(filePath)
                            time.sleep(0.001)
                            with open(filePath, "wb") as f:
                                f.write(bytes(pointCloud, 'utf-8'))
                                f.close()
                            time.sleep(0.001)
                    except:
                        pass
                    time.sleep(0.001)
            else:
                with open(filePath, "wb") as f:
                    f.write(bytes(pointCloud, 'utf-8'))
                    f.close()
                self.pointCloudInit = True
        
    """
        sendMakeReward(self, pointCloud:str, idx:int): Webots Send Make Reward Data to Client
        Input:
            state: the data for reward making
            idx: object idx (int) 
        Output:
            None
    """ 
    def sendMakeReward(self, makeRewardData:str, idx:int, filePath:str=None):
        if filePath is None:
            sendAddress = (self.tar_ip,self.socketPort[idx*6 + 5])
            data = bytes(makeRewardData, 'utf-8')
            self.ProcessSocket_list[idx][5].sendto(data,sendAddress) 
        else:
            if self.makeRewardInit == True:
                while os.path.exists(filePath):
                    time.sleep(0.001)
                with open(filePath, "wb") as f:
                    f.write(bytes(makeRewardData, 'utf-8'))
                    f.close()
                while os.path.exists(filePath):
                    try:
                        while os.path.getsize(filePath) < 1:
                            os.unlink(filePath)
                            time.sleep(0.001)
                            with open(filePath, "wb") as f:
                                f.write(bytes(makeRewardData, 'utf-8'))
                                f.close()
                            time.sleep(0.001)
                    except:
                        pass
                    time.sleep(0.001)
            else:
                with open(filePath, "wb") as f:
                    f.write(bytes(makeRewardData, 'utf-8'))
                    f.close()
                self.makeRewardInit = True
    
    def main(self):
        t1 = threading.Thread(target=self.Get_flags)
        # t1 = Process(target=self.Get_flags)
        t1.start()
        self.Recv_action()

if __name__ == "__main__":
    
    MPR = MultiProcessRecv(5)
    MPR.main()
