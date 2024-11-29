from socket import *
import os
import time
"""
    SendActionSocket:
        1. The class use for sending action/number process/reset signal
        2. Can support 2 modes: Socket mode & File mode(recommand)
"""
class SendActionSocket():
    """
        __init__: Initialize SendActionSocket
        Input:
            ip: target ip address
            port_action: port for sending action
            port_control: port for sending control signal(Not used for current version)
            port_process: port for sending num_process socket
            action_path: path for action file(in file mode)
    """
    def __init__(self,ip='192.168.1.1',port_action=7788,port_control = 7788,port_process = 7789,action_path=None):
        self.udp_sendactionsocket = socket(AF_INET,SOCK_DGRAM)
        self.udp_sendconsocket = socket(AF_INET,SOCK_DGRAM)
        self.udp_recvstartsocket = socket(AF_INET,SOCK_DGRAM)
        self.Target_addr_action = (ip,port_action)
        self.Target_addr_control = (ip,port_control)
        self.Target_addr_process = (ip,port_process)
        self.Recv_addr_process = ("",5000)
        self.action_path = action_path

    def judge_start(self):
        while not os.path.exists("../../Webots_Simulation/traffic_project/Files2Alg/start.txt"):
            time.sleep(0.001)
        while os.path.exists("../../Webots_Simulation/traffic_project/Files2Alg/start.txt"):    
            os.unlink("../../Webots_Simulation/traffic_project/Files2Alg/start.txt")
            time.sleep(0.001)
        return True
    
    """
        send_signal: send action through socket or file
            1. send signal in socket mode
            2. send signal in file mode
        Input:
            sendData: Bytes that to be send
            action: whether signal to be sent is action
            process: whether signal to be sent is num_process
            stuck: whether stuck or not(in file mode)
        Output:
            None
    """
    def send_signal(self,sendData,action=False,process = False,stuck = True):
        if self.action_path is None or process:
            if process:
                self.udp_sendactionsocket.sendto(sendData,self.Target_addr_process)
            else:
                if action:
                    self.udp_sendactionsocket.sendto(sendData,self.Target_addr_action)
                else:
                    self.udp_sendconsocket.sendto(sendData,self.Target_addr_control)
        else:
            with open(self.action_path,"wb") as file:
                file.write(sendData)
                file.close()
            if stuck:
                while os.path.exists(self.action_path):
                    time.sleep(0.001)

    """
        send_action_control: send a pulse signal to inform the env that an action is to be sent
        Input:
            None
        Output:
            void 
    """
    def send_action_control(self):
        self.send_signal(bytes("1\n",'utf-8'),action=False)
        self.send_signal(bytes("0\n",'utf-8'),action=False)

    """
        send_action: send an action to the env server through socket,it can be devided into 2 parts
            1. send a control signal to inform the env server
            2. send action data to the env server
        Input:
            action: action chosen by Agent
        Output:
            Void
    """
    def send_action(self,action:list,step = True,stuck=True):
        if step:
            action.append(0)
        signal = ""
        for i in range(len(action)):
            signal += str(action[i])
            if i != len(action)-1:
                signal += "," 
        signal += "\n"
        signal_bytes = bytes(signal,'utf-8')
        self.send_signal(signal_bytes,action=True,stuck=stuck) 

    """
        send_reset_control: send a pulse signal to reset the env
        Input:
            None
        Output:
            Void
    """
    def send_reset_control(self,id,stuck=True):
        self.send_action([0,0,0,0,1],step=False,stuck = stuck)
    
    """
        judge_empty:Judge if the action file is empty
    """
    def judge_empty(self):
        if not os.path.exists(self.action_path):
            return True
        else:
            return False
        
