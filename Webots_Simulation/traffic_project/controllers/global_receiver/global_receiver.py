# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
from controller import Receiver, Emitter
from controller import Supervisor
import struct
import receiveSocket
import randomorder
import drone_manager
import MultiPortRecv
import time
import json
import random
import os
import platform
import transforms3d as tfs
import sys
sys.path.append("../../config")
import safetyCheck

# check running system
System = platform.system()

# create the Robot instance.
robot = Supervisor()

# get complete path of world file
world_path = robot.getWorldPath()

# read json config file
with open('../../config/env_config.json', 'r') as file:
    configData = json.load(file)
    file.close()
with open('../../config/env_config_backup.json', 'r') as file:
    configData_backup = json.load(file)
    file.close()
    
# config env params
if configData["Sumo_Params"]["fixed_seed"] == True:
    random.seed(configData["Sumo_Params"]["random_seed"])
weatherType = world_path[world_path.find("-")+1:]
if weatherType == "foggy.wbt" and configData["Env_Params"]["foggy_use_default"] == False:
    if configData["Env_Params"]["foggy_visibility_range_random"] == True:
        visible_range = random.uniform(configData["Env_Params"]["foggy_visibility_range_min"],configData["Env_Params"]["foggy_visibility_range_min"])
    else:
        visible_range = configData["Env_Params"]["foggy_visibility_range_fixed"]
    robot.getFromDef("fog").getField("visibilityRange").setSFFloat(float(visible_range))
    
if configData["Env_Params"]["background_luminosity_random"] == True:
    bgl = random.uniform(configData["Env_Params"]["bgl_random_min"],configData["Env_Params"]["bgl_random_max"])
else:
    bgl = robot.getFromDef("tbg").getField("luminosity").getSFFloat() + configData["Env_Params"]["bgl_incremental"]
robot.getFromDef("tbg").getField("luminosity").setSFFloat(float(bgl))

if configData["Env_Params"]["backgroundLight_luminosity_random"] == True:
    bgLl = random.uniform(configData["Env_Params"]["bgLl_random_min"],configData["Env_Params"]["bgLl_random_max"])
else:
    bgLl = robot.getFromDef("tbgl").getField("luminosity").getSFFloat() + configData["Env_Params"]["bgLl_incremental"]
robot.getFromDef("tbgl").getField("luminosity").setSFFloat(float(bgLl))
    
    
# safety check
if configData["Sumo_Params"]["rou_update"] == False:
    configData["Sumo_Params"]["rou_update"] = safetyCheck.checkSumoUpdate(configData,configData_backup)
    if world_path != configData_backup["World_Path"]:
        configData["Sumo_Params"]["rou_update"] = True
configData["Simulation_Mode"] = safetyCheck.check(str(configData["Simulation_Mode"]),safetyCheck.SIMULATION_MODE)
configData["Tracker_Def"] = safetyCheck.check(str(configData["Tracker_Def"]),safetyCheck.TRACKER_DEF)
configData["Tracking_Object"] = safetyCheck.check(configData["Tracking_Object"],safetyCheck.TRACKING_OBJECT)
configData["Reward_Config"]["reward_mode"] = safetyCheck.check(configData["Reward_Config"]["reward_mode"],safetyCheck.REWARD_MODE)
configData["Sumo_Params"]["car_type"] = safetyCheck.check(configData["Sumo_Params"]["car_type"],safetyCheck.CAR_TYPE)

# get tracker def
trackerDef = str(configData["Tracker_Def"])
    
# set config data to sumo interface
SUMO_Interface = robot.getFromDef("SUMO_INTERFACE")

SUMO_Interface.getField("port").setSFInt32(configData["Config_Agen_Num_Port"])

if configData["Tracking_Object"] == "SUMO_VEHICLE":
    SUMO_Interface.getField("maxVehicles").setSFInt32(configData["Sumo_Params"]["max_sumo_car"])
else:
    SUMO_Interface.getField("maxVehicles").setSFInt32(0)
    
if configData["Sumo_Params"]["fixed_seed"] == True:
    SUMO_Interface.getField("seed").setSFInt32(configData["Sumo_Params"]["random_seed"])
else:
    SUMO_Interface.getField("seed").setSFInt32(0)

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())
# emitter node
emitter = robot.getDevice("emitter")

# the global init state is one
global_state = 1
global_init = False

# seperate different simulation modes
FollowPort = None
file_path = world_path[:world_path.find('-')] + '_net'
car_import_group_num = configData["Sumo_Params"]["car_group_num"]

# clear cache files
if System == "Linux":
        os.system("rm -rf ../../Files2Alg/*.txt")
        os.system("rm -rf ../../Files2Alg/*.jpeg")
        os.system("rm -rf ../../cache/*.txt")
        os.system("rm -rf ../../cache/*.jpeg")
elif System == "Windows":
    os.system("del /s /q /f ../../Files2Alg/*.txt")
    os.system("del /s /q /f ../../Files2Alg/*.jpeg")
    os.system("del /s /q /f ../../cache/*.txt")
    os.system("del /s /q /f ../../cache/*.jpeg")
    
if configData["Simulation_Mode"] == "demo":
    drone_manager.droneManager(trackerDef, robot, timestep, 0, [], configData, [], {}, [False], weatherType)
    data = [0.] * 6
    data[4] = -1 # inited to -1
    data[5] = -1
    # FollowPort = receiveSerial.SerialPort(6,data)
    FollowPort = receiveSocket.SocketPort(6,data,7790)
    getFromPort = [0.] * FollowPort.data_size
    getFromPortStr = ["0"] * FollowPort.data_size
    getFromPort[4] = -1
    getFromPort[5] = -1
    if configData["Tracking_Object"] == "SUMO_VEHICLE":
        # if configData["Sumo_Random_Mode"] == 1:
        #     randomorder.sumo_rou_random(file_path, int(4), configData["Sumo_Params"])
        # elif configData["Sumo_Random_Mode"] == 2:
        #     randomorder.sumo_rou_random_os(file_path, int(4), System, configData["Sumo_Params"])
        randomorder.sumo_rou_random_os(file_path, int(car_import_group_num), System, configData["Sumo_Params"])
        configData["Sumo_Params"]["car_group_num"] = int(car_import_group_num)
elif configData["Simulation_Mode"] == "train":
    # multiple communications
    multiCom = MultiPortRecv.MultiProcessRecv(trackerDef,configData["Socket_Ip"],5,configData["Control_Frequence"],configData["Config_Agen_Num_Port"],configData["Verbose"])
    multiCom.main()
    # activate map random init
    if configData["Tracking_Object"] == "SUMO_VEHICLE":
        # if configData["Sumo_Random_Mode"] == 1:
        #     randomorder.sumo_rou_random(file_path, int(multiCom.Number_process*3), configData["Sumo_Params"])
        # elif configData["Sumo_Random_Mode"] == 2:
        #     randomorder.sumo_rou_random_os(file_path, int(multiCom.Number_process*3), System, configData["Sumo_Params"])
        if configData["Sumo_Params"]["fixed_car_group_num"] == True and car_import_group_num >= multiCom.Number_process*3:
            randomorder.sumo_rou_random_os(file_path, int(car_import_group_num), System, configData["Sumo_Params"])
            configData["Sumo_Params"]["car_group_num"] = int(car_import_group_num)
        else:
            configData["Sumo_Params"]["rou_update"] = True
            randomorder.sumo_rou_random_os(file_path, int(multiCom.Number_process*3), System, configData["Sumo_Params"])
            configData["Sumo_Params"]["car_group_num"] = int(multiCom.Number_process*3)
    # according to the number of process ,establish multiple objects
    droneM = []
    # sumo shared storage section
    sumoList = []
    sumoDictionary = {}
    sumoGetCarFlag = [False]*multiCom.Number_process
    for i in range(multiCom.Number_process):
        droneM.append(drone_manager.droneManager(trackerDef, robot, timestep, i, multiCom, configData, sumoList, sumoDictionary, sumoGetCarFlag, weatherType))
elif configData["Simulation_Mode"] == "video":
    # clear space
    delete_count = 0
    while os.path.exists("../../Videos/" + "DRONE" + str(delete_count)):
        if System == "Linux":
            os.system("rm -rf ../../Videos/" + "DRONE" + str(delete_count))
        elif System == "Windows":
            os.system("del /s /q /f ../../Videos/" + "DRONE" + str(delete_count))
        delete_count = delete_count + 1
    delete_count = 0
    while os.path.exists("../../Videos/" + "CAR" + str(delete_count)):
        if System == "Linux":
            os.system("rm -rf ../../Videos/" + "CAR" + str(delete_count))
        elif System == "Windows":
            os.system("del /s /q /f ../../Videos/" + "CAR" + str(delete_count))
        delete_count = delete_count + 1
    # create directories to contain frames
    for i in range(configData["Out_Video"]["channels"]):
        os.mkdir("../../Videos/" + str(trackerDef) + str(i))    
        
    # activate map random init
    if configData["Tracking_Object"] == "SUMO_VEHICLE":
        # if configData["Sumo_Random_Mode"] == 1:
        #     randomorder.sumo_rou_random(file_path, int(configData["Out_Video"]["channels"]*2), configData["Sumo_Params"])
        # elif configData["Sumo_Random_Mode"] == 2:
        #     randomorder.sumo_rou_random_os(file_path, int(configData["Out_Video"]["channels"]*2), System, configData["Sumo_Params"])
        if configData["Sumo_Params"]["fixed_car_group_num"] == True and car_import_group_num >= configData["Out_Video"]["channels"]*3:
            randomorder.sumo_rou_random_os(file_path, int(car_import_group_num), System, configData["Sumo_Params"])
            configData["Sumo_Params"]["car_group_num"] = int(car_import_group_num)
        else:
            configData["Sumo_Params"]["rou_update"] = True
            randomorder.sumo_rou_random_os(file_path, int(configData["Out_Video"]["channels"]*3), System, configData["Sumo_Params"])
            configData["Sumo_Params"]["car_group_num"] = int(configData["Out_Video"]["channels"]*3)
    # according to the number of process ,establish multiple objects
    droneM = []
    # sumo shared storage section
    sumoList = []
    sumoDictionary = {}
    sumoGetCarFlag = [False]*configData["Out_Video"]["channels"]
    for i in range(configData["Out_Video"]["channels"]):
        droneM.append(drone_manager.droneManager(trackerDef, robot, timestep, i, None, configData, sumoList, sumoDictionary, sumoGetCarFlag, weatherType))
  
configData["World_Path"] = world_path
with open('../../config/env_config_backup.json', 'w') as file:
    json.dump(configData,file)
    file.close() 

# Main loop:
# - perform simulation steps until Webots is stopping the controller
if configData["Simulation_Mode"] == "demo":
    while robot.step(timestep) != -1:
        getFromPort, getFromPortStr = FollowPort.read()
        for i in range(FollowPort.data_size):
            if getFromPort[i] == None:
                if i < 4:
                    getFromPort[i] = 0
                else:
                    getFromPort[i] = -1
        message = struct.pack("ffffff",getFromPort[0],getFromPort[1],getFromPort[2],getFromPort[3],getFromPort[4],getFromPort[5])
        emitter.setChannel(1)
        emitter.send(message)
        pass
elif configData["Simulation_Mode"] == "train":
    while True:
        if global_init == False:
            global_init = True
            init_count = 0
            # firstly run steps for sumo to prepare for the cars
            while init_count < (int(configData["Drone_Random_Config"]["start_time_bias_ms"]) + 6*multiCom.Number_process):
                init_count = init_count + 1
                while robot.step(timestep) == -1: # step until simulation is running
                    pass 
            for drone in droneM:
                drone.loop.start()
        
        # if step count larger than 0 then run a real step
        run_step = False
        for i in range(multiCom.Number_process):
            if multiCom.is_step[i] > 0:
                run_step = True
            
        if run_step == True:
            while robot.step(timestep) == -1: # step until simulation is running
                pass
            for drone in droneM:
                drone.runMultiState(1)
elif configData["Simulation_Mode"] == "video":
    while True:
        if global_init == False:
            global_init = True
            init_count = 0
            # firstly run steps for sumo to prepare for the cars
            while init_count < (int(configData["Drone_Random_Config"]["start_time_bias_ms"]) + 4*configData["Out_Video"]["channels"]):
                init_count = init_count + 1
                while robot.step(timestep) == -1: # step until simulation is running
                    pass 
            for drone in droneM:
                drone.videoloop.start()
        
        # if step count larger than 0 then run a real step
        run_step = False
        for i in range(configData["Out_Video"]["channels"]):
            run_step = True
            
        if run_step == True:
            while robot.step(timestep) == -1: # step until simulation is running
                pass
            for drone in droneM:
                drone.runMultiState(1)

                
        

                
# Enter here exit cleanup code.
