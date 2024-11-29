import sys
sys.path.append("../../libraries")
sys.path.append("../SUMOGod")
from controller import robot
from controller import Receiver, Emitter
from controller import Supervisor
import struct
import SUMOGod
import threading
import time
import random
import os
import platform
import logging
import MultiPortRecv
import socket
import math


class droneManager:
    '''
    description: a manager to support an agent including communication, random init and control
    param {*} self
    param {Supervisor} supervisor: a webots supervisor node
    param {*} timeStep: simulation running timestep
    param {*} id: drone id
    param {*} recCtrlPort: multiple process communication port
    param {*} configData: simulation config data
    param {*} sumoList: a list that manage target car
    param {*} sumoDict: a dictionary that manage target car
    param {*} sumoGetFlag: a list that judges whether the cars are allocated 
    return {*}
    '''    
    def __init__(self, trackerDef:str, supervisor:Supervisor, timeStep, id, recCtrlPort, configData, sumoList, sumoDict, sumoGetFlag, weatherType):
        # get supervisor node
        self.supervisor = supervisor
        # get timeStep value
        self.timeStep = timeStep
        # get communication port
        self.recCtrlPort = recCtrlPort
        # get drone id
        self.id = id
        # get configuration
        self.configData = configData
        # get wheather type
        self.weatherType = weatherType
        # define sumoGod
        if configData["Sumo_Params"]["fixed_seed"] == True:
            random.seed(configData["Sumo_Params"]["random_seed"])
            self.sumoGod = SUMOGod.getSumoCarNode(id, sumoList, sumoDict, sumoGetFlag, configData["Sumo_Params"]["random_seed"])
        else:
            self.sumoGod = SUMOGod.getSumoCarNode(id, sumoList, sumoDict, sumoGetFlag)
        # create new drone node
        self.trackerDef = trackerDef
        self.droneDef = trackerDef + str(id)
        if trackerDef == 'DRONE':
            droneString = 'DEF ' + self.droneDef + ' M100 { controller "drone_ctrl2" customData "online" supervisor TRUE }'
        elif trackerDef == 'CAR':
            droneString = 'DEF ' + self.droneDef + ' SimpleRobot { controller "simpleCar_ctrl" }'
        rootChildrenField = self.supervisor.getRoot().getField('children')
        rootChildrenField.importMFNodeFromString(id, droneString)
        self.drone = self.supervisor.getFromDef(self.droneDef)
        droneTrV = self.drone.getField('translation').getSFVec3f()
        droneTrV[0] = droneTrV[0] + 1 * id
        droneTrV[1] = droneTrV[1] + 1 * id
        self.drone.getField('translation').setSFVec3f(droneTrV)
        # Logging
        if self.configData["Verbose"] == True:
            MultiPortRecv.setup_logger(trackerDef+str(id),"../../logs/Agent"+str(id)+".log")
            self.logger = logging.getLogger(trackerDef+str(id))
        # init communications
        self.getFromActionPort = [0.] * 5
        # init action files
        self.actionActivateFile(0)
        # prepare main_loop state machine status
        self.machine_state = 1
        # multiprocess actuate flag
        self.multi_state = 0
        # drone camera pitch angle
        self.camera_pitch = 1
        # establish drone manager threading
        self.loop = threading.Thread(target=self.mainLoop)
        self.videoloop = threading.Thread(target=self.mainLoopForVideo)
        
    '''
    description: update action data from multiple ALG
    param {*} self
    return {*}
    '''
    def actionUpdate(self):
        self.getFromActionPort = self.recCtrlPort.getAction(self.id)      
        
    '''
    description: use emitter to set action to drone controller
    param {*} self
    param {Emitter} emitter
    param {*} step_count
    return {*}
    '''
    def actionActivate(self, emitter:Emitter, step_count):
        action_message = struct.pack("fffff",self.getFromActionPort[0],self.getFromActionPort[1],self.getFromActionPort[2],self.getFromActionPort[3],step_count)
        emitter.send(action_message) 
        
        
    '''
    description: use file io to set action to drone controller
    param {*} self
    param {*} step_count
    return {*}
    '''
    def actionActivateFile(self, step_count):
        with open("../../cache/" + self.droneDef + "_Global2Ctrl.txt", "w") as f:
            actionStr = str(self.getFromActionPort[0]) + "\n" + str(self.getFromActionPort[1]) + "\n" + str(self.getFromActionPort[2]) + "\n" + str(self.getFromActionPort[3]) + "\n" + str(step_count) + "\n"
            f.write(actionStr)
            f.close()
        
        
    '''
    description: return state reward done / reward params / point cloud / image to ALG
    param {*} self
    return {*}
    '''
    def returnState(self, step_count):
        if self.configData["Verbose"] == True:
            self.logger.info(str(step_count))
        # send state reward and done
        with open("../../cache/" + self.droneDef + "_Ctrl2Global.txt", "r") as f:
            data = f.readline()
            f.close()
        while len(data) < 2:
            with open("../../cache/" + self.droneDef + "_Ctrl2Global.txt", "r") as f:
                data = f.readline()
                f.close()
        if self.configData["Verbose"] == True:
            self.logger.info(data)
        self.recCtrlPort.sendState(data,self.id,"../../Files2Alg/" + self.droneDef + "_Ctrl2Global.txt")
        # if config files defines,then send below data
        if self.configData["Customized_Rewards"]:
            with open("../../cache/" + self.droneDef + "_Ctrl2GlobalR.txt", "r") as f:
                data = f.readline()
                f.close()
            while len(data) < 2:
                with open("../../cache/" + self.droneDef + "_Ctrl2GlobalR.txt", "r") as f:
                    data = f.readline()
                    f.close()
            if self.configData["Verbose"] == True:
                self.logger.info(data)
            self.recCtrlPort.sendMakeReward(data,self.id,"../../Files2Alg/" + self.droneDef + "_RewardParams.txt")
        if self.configData["Lidar_Enable"]:
            with open("../../cache/" + self.droneDef + "_LidarCloud.txt", "r") as f:
                data = f.readline()
                f.close()
            while len(data) < 2:
                with open("../../cache/" + self.droneDef + "_LidarCloud.txt", "r") as f:
                    data = f.readline()
                    f.close()
            self.recCtrlPort.sendPointCloud(data,self.id,"../../Files2Alg/" + self.droneDef + "_PointCloud.txt")
        # send camera graphs
        self.recCtrlPort.sendImage("../../cache/" + self.droneDef + "_VideoFrame.jpeg",
                                   self.id,
                                   "../../Files2Alg/" + self.droneDef + "_VideoFrame.jpeg",
                                   "../../Files2Alg/" + self.droneDef + "_VideoFrame.txt")
            
    '''
    description: return only image to ALG
    param {*} self
    return {*}
    '''
    def returnOnlyImage(self):
        # send camera graphs
        self.recCtrlPort.sendImage("../../cache/" + self.droneDef + "_VideoFrame.jpeg",
                                   self.id,
                                   "../../Files2Alg/" + self.droneDef + "_VideoFrame.jpeg",
                                   "../../Files2Alg/" + self.droneDef + "_VideoFrame.txt")
            
    '''
    description: drone get target car init
    param {*} self
    return {*}
    '''
    def init(self):
        if self.configData["Drone_Random_Config"]["view_pitch_random"] == False:
            self.camera_pitch = self.configData["Drone_Random_Config"]["view_pitch_fixed"]
        else:
            self.camera_pitch = random.uniform(self.configData["Drone_Random_Config"]["view_pitch_random_min"],self.configData["Drone_Random_Config"]["view_pitch_random_max"])
        
        if self.configData["Drone_Random_Config"]["horizon_bias_random"] == False:
            horizon_bias = self.configData["Drone_Random_Config"]["horizon_bias_fixed"]
        else:
            if self.configData["Drone_Random_Config"]["horizon_bias_multilateral"] == False:
                horizon_bias = random.uniform(self.configData["Drone_Random_Config"]["horizon_bias_random_min"],self.configData["Drone_Random_Config"]["horizon_bias_random_max"])
            else:
                horizon_side = random.choice([1,-1])
                horizon_bias = horizon_side * random.uniform(abs(self.configData["Drone_Random_Config"]["horizon_bias_random_min"]),abs(self.configData["Drone_Random_Config"]["horizon_bias_random_max"]))    
        
        if self.configData["Drone_Random_Config"]["verticle_bias_random"] == False:
            verticle_bias = self.configData["Drone_Random_Config"]["verticle_bias_fixed"]
        else:
            if self.configData["Drone_Random_Config"]["verticle_bias_multilateral"] == False:
                verticle_bias = random.uniform(self.configData["Drone_Random_Config"]["verticle_bias_random_min"],self.configData["Drone_Random_Config"]["verticle_bias_random_max"])
            else:
                verticle_side = random.choice([1,-1])
                verticle_bias = verticle_side * random.uniform(abs(self.configData["Drone_Random_Config"]["verticle_bias_random_min"]),abs(self.configData["Drone_Random_Config"]["verticle_bias_random_max"]))
            
            
        if self.configData["Drone_Random_Config"]["height_random"] == False:
            transScale = self.configData["Drone_Random_Config"]["height_fixed"]
        else:
            transScale = random.uniform(self.configData["Drone_Random_Config"]["height_random_min"],self.configData["Drone_Random_Config"]["height_random_max"])
        
        if self.configData["Tracking_Object"] == str("SUMO_VEHICLE"):
            transVector = [-math.tan(abs(1.5708-self.camera_pitch))*transScale-1+verticle_bias, horizon_bias, transScale]
        else:
            transVector = [-math.tan(abs(1.5708-self.camera_pitch))*transScale+verticle_bias, horizon_bias, transScale]
        
        if self.configData["Drone_Random_Config"]["direction_random"] == False:
            rotateAngle = self.configData["Drone_Random_Config"]["direction_fixed"]
        else:
            if self.configData["Drone_Random_Config"]["direction_random_multilateral"] == False:
                rotateAngle = random.uniform(self.configData["Drone_Random_Config"]["direction_random_min"],self.configData["Drone_Random_Config"]["direction_random_max"])
            else:
                rotateAngle = random.choice([1,-1]) * random.uniform(abs(self.configData["Drone_Random_Config"]["direction_random_min"]),abs(self.configData["Drone_Random_Config"]["direction_random_max"]))
                
        self.updateInitParams(self.camera_pitch, rotateAngle)
        
        if self.configData["Sumo_Params"]["fixed_color"] is True and self.configData["Sumo_Params"]["car_type"] != "motorcycle" and self.configData["Tracking_Object"] == "SUMO_VEHICLE":
            colorList = list(self.configData["Sumo_Params"]["normalize_color"])
        else:
            colorList = None
        return self.sumoGod.SingleProcessRandomInit(self.supervisor, self.timeStep, self.drone, transVector, rotateAngle, self.configData["Tracking_Object"], colorList)
        
    '''
    description: reset car controller
    param {*} self
    return {*}
    '''
    def reset(self):
        if self.configData["Verbose"] == True:
            print("\nid:   ",self.id,"    reset: rrrrrrrrrrrrrrrr")
        self.resetPlugin()
        self.drone.restartController()
        
    '''
    description: write files to update machine state
    param {*} self
    param {*} filePath: the path to write files
    return {*}
    '''
    def updateMachineState(self):
        self.recCtrlPort.sendMachine(self.machine_state,self.id,"../../cache/" + self.droneDef + "_MachineState.txt")
        
    '''
    description: write files to update machine state
    param {*} self
    param {*} filePath: the path to write files
    return {*}
    '''
    def updateInitParams(self, cameraPitch, direction):
        with open("../../cache/" + self.droneDef + "_InitParams.txt", "w") as f:
            f.write(str(cameraPitch) + "\n" + str(direction) + "\n")
            f.close()
            
        
    '''
    description: 1.Drone manager mainLoop, which manage the state machine.
                 2.Firstly init the drone and random select a available target car. Move the drone above it.
                 3.Then run into the step mode, which continuously communicates with ALG and controlled by ALG.
                 4.While satisfying the reset condition, get into reset mode and reset.
                 5.After reset, return to the init mode
    param {*} self
    return {*}
    '''
    def mainLoop(self):
        self.initTime = time.time()
        self.lastTime = self.initTime
        while True:
            self.initTime = time.time()
            self.updateMachineState()
            self.recCtrlPort.keepSocketRunning()
            self.actionUpdate()
            
            if self.multi_state == 1:
                if self.machine_state == 1:
                    self.recCtrlPort.is_reset[self.id] = False
                    self.recCtrlPort.is_step[self.id] = 0
                    self.step_count = 0
                    if self.init():
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("drone finish sumo init")
                        # self.returnOnlyImage()
                        self.returnState(self.step_count)
                        self.machine_state = 2 # init come to an end and transfer to steps
                elif self.machine_state == 2:
                    self.sumoGod.ResetSumoDictionary()
                    if self.recCtrlPort.is_reset[self.id] == True and self.step_count > 100:
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("begin to reset")
                        self.reset()
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("finish reset")
                        self.sumoGod.delectDefList()
                        self.recCtrlPort.is_reset[self.id] = False
                        self.machine_state = 1 # remember to reset
                    else:
                        self.actionActivateFile(self.step_count)
                        if self.recCtrlPort.is_step[self.id] == 1:
                            # if self.configData["Verbose"] == True:
                            #     self.logger.info("return states reward done")
                            self.returnState(self.step_count)
                        # reset step counts that have been actuated
                        self.recCtrlPort.is_step[self.id] = self.recCtrlPort.is_step[self.id] - 1
                        if self.recCtrlPort.is_step[self.id] < 0:
                            self.recCtrlPort.is_step[self.id] = 0
                        # complete a step count add one
                        self.step_count = self.step_count + 1
                        self.multi_state = 0
                        
    def mainLoopForVideo(self):
        self.initTime = time.time()
        self.lastTime = self.initTime
        is_step = [0]*self.configData["Out_Video"]["channels"] # Whether Trigger a step
        is_reset = [False]*self.configData["Out_Video"]["channels"] # Whether Trigger a reset
        episode = 0
        udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        while True:
            self.initTime = time.time()
            sendAddress = (self.configData["Socket_Ip"],self.configData["Config_Agen_Num_Port"])
            data = bytes(str(0) + "\n", 'utf-8')
            udp_socket.sendto(data, sendAddress)

            if self.multi_state == 1:
                if self.machine_state == 1:
                    is_reset[self.id] = False
                    is_step[self.id] = 1
                    self.step_count = 0
                    System = platform.system()
                    if not os.path.exists("../../Videos/"+self.trackerDef+str(self.id)+"/episode"+str(episode)):
                        os.mkdir("../../Videos/"+self.trackerDef+str(self.id)+"/episode"+str(episode))
                    else:
                        if System == "Linux":
                            os.system("rm -rf ../../Videos/" + self.trackerDef + str(self.id) + "/episode" + str(episode) + "/*.jpeg")
                        elif System == "Windows":
                            os.system("del /s /q /f ../../Videos/" + self.trackerDef + str(self.id) + "/episode" + str(episode) + "/*.jpeg")
                    episode = episode + 1
                    if self.init():
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("drone finish sumo init")
                        with open("../../cache/" + self.droneDef + "_Ctrl2Global.txt", "r") as f:
                            data = f.readline()
                            f.close()
                        is_reset[self.id] = int(data.rstrip().split(',')[-1])
                        self.machine_state = 2 # init come to an end and transfer to steps
                elif self.machine_state == 2:
                    self.sumoGod.ResetSumoDictionary()
                    if is_reset[self.id] == True and self.step_count > 100:
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("begin to reset")
                        self.reset()
                        # if self.configData["Verbose"] == True:
                        #     self.logger.info("finish reset")
                        self.sumoGod.delectDefList()
                        is_reset[self.id] = False
                        self.machine_state = 1 # remember to reset
                    else:
                        if self.configData["Out_Video"]["random_action"] == False:
                            self.sumoGod.MoveDroneToCar(self.sumoGod.currentUseCarNode, self.drone, self.sumoGod.transVector, self.sumoGod.rotateAngle, False)
                        if is_step[self.id] == 1:
                            # if self.configData["Verbose"] == True:
                            #     self.logger.info("return states reward done")
                            with open("../../cache/" + self.droneDef + "_Ctrl2Global.txt", "r") as f:
                                data = f.readline()
                                f.close()
                        if len(data)>10:
                            is_reset[self.id] = int(data.rstrip().split(',')[-1])
                        # reset step counts that have been actuated
                        is_step[self.id] = 1
                        # complete a step count add one
                        self.step_count = self.step_count + 1
                        self.multi_state = 0
            
    '''
    description: An external interface to start loops
    param {*} self
    param {*} state: if state is set to 1, the mainloop will actuate one loop
    return {*}
    '''
    def runMultiState(self, state):
        # If the thread is not finished, it blocks and waits for the thread to finish.
        while self.multi_state != 0:
            pass
        # Threads can be opened for a new run
        self.multi_state = state
        
    '''
    description: Other configurations while reseting agents
    param {*} self
    return {*}
    '''
    def resetPlugin(self):
        if self.configData["Env_Params"]["enable_each_reset"] == True:
            if self.weatherType == "foggy.wbt" and self.configData["Env_Params"]["foggy_use_default"] == False:
                if self.configData["Env_Params"]["foggy_visibility_range_random"] == True:
                    visible_range = random.uniform(self.configData["Env_Params"]["foggy_visibility_range_min"],self.configData["Env_Params"]["foggy_visibility_range_min"])
                else:
                    visible_range = self.configData["Env_Params"]["foggy_visibility_range_fixed"]
                self.supervisor.getFromDef("fog").getField("visibilityRange").setSFFloat(float(visible_range))
                
            if self.configData["Env_Params"]["background_luminosity_random"] == True:
                bgl = random.uniform(self.configData["Env_Params"]["bgl_random_min"],self.configData["Env_Params"]["bgl_random_max"])
            else:
                bgl = self.supervisor.getFromDef("tbg").getField("luminosity").getSFFloat() + self.configData["Env_Params"]["bgl_incremental"]
            self.supervisor.getFromDef("tbg").getField("luminosity").setSFFloat(float(bgl))

            if self.configData["Env_Params"]["backgroundLight_luminosity_random"] == True:
                bgLl = random.uniform(self.configData["Env_Params"]["bgLl_random_min"],self.configData["Env_Params"]["bgLl_random_max"])
            else:
                bgLl = self.supervisor.getFromDef("tbgl").getField("luminosity").getSFFloat() + self.configData["Env_Params"]["bgLl_incremental"]
            self.supervisor.getFromDef("tbgl").getField("luminosity").setSFFloat(float(bgLl))
        else:
            pass