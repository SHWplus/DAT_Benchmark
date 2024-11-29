import socket
import os
import threading

class SocketPort:
    def __init__(self, _data_size, _init_list, id):
        command = 'ifconfig enp108s0 192.168.1.1 netmask 255.255.255.0'
        sudo_password = '1210'
        sudo_command = f'echo {sudo_password} | sudo -S {command}'
        os.system(sudo_command)
        # os.system('ifconfig enp108s0 192.168.1.1 netmask 255.255.255.0')
        
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udp_socket.bind(('',id))
        
        self.data_size = int(_data_size)
        
        ### Set Socket Port#################
        self.s = b''
        self.slist = []
        self.data = _init_list
        self.sdata = ["0"] * self.data_size

        #### New Thread Start  #####################
        self.socket_loop = threading.Thread(target=self._socket_update)
        self.socket_loop.start()
        
        self.is_rec = False
        self.is_step = 0
        self.is_reset = False
        
           
    def _socket_update(self):
        while True:
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
                    if self.data[self.data_size-1] == 1.0:
                        self.is_step = self.is_step + 1
                    elif self.data[self.data_size-1] == 2.0:
                        self.is_reset = True
                        print("fking init state!!!!!!!!!!!!!!!!!!!!!!44")
                        
        self.udp_socket.close()
          
    def read(self):
        return self.data, self.sdata




