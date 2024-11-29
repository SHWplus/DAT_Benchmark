import math
import json
import random
import sys
import sys
sys.path.append("../../config")
import safetyCheck

def check(input:str, container:list):
        is_contain = False
        for i in range(len(container)):
            if input == container[i]:
                is_contain = True
        if is_contain == True:
            return input
        else:
            return container[0]

class SumoSupervisorPlugin:
    def __init__(self, supervisor, traci, net):
        # read json config file
        with open('../../config/env_config.json', 'r') as file:
            self.configData = json.load(file)
            file.close()
        # safety check
        self.configData["Simulation_Mode"] = check(str(self.configData["Simulation_Mode"]),safetyCheck.SIMULATION_MODE)
        self.configData["Tracking_Object"] = check(self.configData["Tracking_Object"],safetyCheck.TRACKING_OBJECT)
        self.configData["Reward_Config"]["reward_mode"] = check(self.configData["Reward_Config"]["reward_mode"],safetyCheck.REWARD_MODE)
        self.configData["Sumo_Params"]["car_type"] = check(self.configData["Sumo_Params"]["car_type"],safetyCheck.CAR_TYPE)
        if self.configData["Tracking_Object"] != "SUMO_VEHICLE":
            self.supervisor = supervisor
            self.isInit = False
            self.xOffset = -net.getLocationOffset()[0]
            self.yOffset = -net.getLocationOffset()[1]
            # get all available edges
            self.edges = net.getEdges()
            # record start points and end points
            self.path_start_end = []
            for edge in self.edges:
                # get start node and end node
                start_node = edge.getFromNode()
                end_node = edge.getToNode()
                # get coordinaries
                start_coords = start_node.getCoord()  # (x, y, z)
                end_coords = end_node.getCoord()      # (x, y, z)
                self.path_start_end.append((edge.getID(), start_coords, end_coords))
            # print relative informations
            for edge_id, start_coords, end_coords in self.path_start_end:
                print(f"Path ID: {edge_id}, Start Coordinates: {start_coords}, End Coordinates: {end_coords}")
            # get the init time from configData
            self.last_time = float(self.configData["Drone_Random_Config"]["start_time_bias_ms"]) * 0.001
            # get webots root children field
            self.rootChildField = self.supervisor.getRoot().getField('children')
            # obj num management
            self.objIDlist = []
            self.objInfo = {}
    
    def run(self, ms):
        if self.configData["Tracking_Object"] != "SUMO_VEHICLE":
            self.t = self.supervisor.getTime()
            # random choose edges for object settings
            if (self.t-self.last_time) > self.configData["Other_Params"]["obj_import_interval"] or (self.t > float(self.configData["Drone_Random_Config"]["start_time_bias_ms"]) * 0.001 and self.isInit == False):
                if self.isInit == True:
                    self.last_time = self.t
                self.isInit = True
                # firstly manage obj number
                self.collect_obj(self.configData["Tracking_Object"])
                add_obj_number = 0
                update_obj_number = 0
                if (self.configData["Other_Params"]["max_obj_num"] - len(self.objIDlist)) < self.configData["Other_Params"]["import_group_num"]:
                    add_obj_number = self.configData["Other_Params"]["max_obj_num"] - len(self.objIDlist)
                    update_obj_number = self.configData["Other_Params"]["import_group_num"] - add_obj_number
                else:
                    add_obj_number = self.configData["Other_Params"]["import_group_num"]
                    update_obj_number = 0
                if add_obj_number > 0:
                    random_edges = random.sample(self.path_start_end,add_obj_number)
                    addCount = 0
                    for edge_id, start_coords, end_coords in random_edges:
                        addCount = addCount + 1
                        length = math.sqrt(math.pow(end_coords[0]-start_coords[0],2)+math.pow(end_coords[1]-start_coords[1],2))
                        dirVector = [end_coords[0]-start_coords[0],end_coords[1]-start_coords[1]]
                        # randomly get a scale between [0,1]
                        scale = random.uniform(0,1)
                        setPoint = [start_coords[0]+scale*dirVector[0]+self.xOffset,start_coords[1]+scale*dirVector[1]+self.yOffset]
                        normalizeDirT = [dirVector[1]/length,dirVector[0]/length]
                        if self.configData["Other_Params"]["obj_edge_distribution_random"] == False:
                            Tscale = self.configData["Other_Params"]["obj_edge_distribution_fixed"]
                        else:
                            if self.configData["Other_Params"]["obj_edge_distribution_multilateral"] == False:
                                Tscale = random.uniform(self.configData["Other_Params"]["obj_edge_distribution_min"], self.configData["Other_Params"]["obj_edge_distribution_max"])
                            else:
                                Tscale = random.uniform(abs(self.configData["Other_Params"]["obj_edge_distribution_min"]), abs(self.configData["Other_Params"]["obj_edge_distribution_max"]))
                                Tscale = Tscale * random.choice([-1,1])
                        setPoint[0] += normalizeDirT[0] * Tscale
                        setPoint[1] += normalizeDirT[1] * Tscale
                        if len(self.objIDlist) == 0:
                            countOffset = 0
                        else:
                            countOffset = max(self.objIDlist)
                        self.add_obj(self.configData["Tracking_Object"],countOffset + addCount,setPoint,1.3,-1)
                if update_obj_number > 0:
                    self.collect_obj(self.configData["Tracking_Object"])
                    random_edges = random.sample(self.path_start_end,update_obj_number)
                    addCount = 0
                    for edge_id, start_coords, end_coords in random_edges:
                        addCount = addCount + 1
                        length = math.sqrt(math.pow(end_coords[0]-start_coords[0],2)+math.pow(end_coords[1]-start_coords[1],2))
                        dirVector = [end_coords[0]-start_coords[0],end_coords[1]-start_coords[1]]
                        # randomly get a scale between [0,1]
                        scale = random.uniform(0,1)
                        setPoint = [start_coords[0]+scale*dirVector[0]+self.xOffset,start_coords[1]+scale*dirVector[1]+self.yOffset]
                        normalizeDirT = [dirVector[1]/length,dirVector[0]/length]
                        if self.configData["Other_Params"]["obj_edge_distribution_random"] == False:
                            Tscale = self.configData["Other_Params"]["obj_edge_distribution_fixed"]
                        else:
                            if self.configData["Other_Params"]["obj_edge_distribution_multilateral"] == False:
                                Tscale = random.uniform(self.configData["Other_Params"]["obj_edge_distribution_min"], self.configData["Other_Params"]["obj_edge_distribution_max"])
                            else:
                                Tscale = random.uniform(abs(self.configData["Other_Params"]["obj_edge_distribution_min"]), abs(self.configData["Other_Params"]["obj_edge_distribution_max"]))
                                Tscale = Tscale * random.choice([-1,1])
                        setPoint[0] += normalizeDirT[0] * Tscale
                        setPoint[1] += normalizeDirT[1] * Tscale
                        if len(self.objIDlist) == 0:
                            countOffset = 0
                            objName = None
                        else:
                            countOffset = max(self.objIDlist)
                            # search for min num and delete it
                            objName = min(self.objIDlist)
                            self.objIDlist = [x for x in self.objIDlist if x != objName]
                        if self.configData["Tracking_Object"] == "Pedestrian":
                            objNode,objDef,objIndex = self.getObjInfoByName(str(objName))
                            self.rootChildField.removeMF(objIndex)
                            self.add_obj(self.configData["Tracking_Object"],countOffset + 1,setPoint,1.3,-1)
                            self.collect_obj(self.configData["Tracking_Object"])
                        else:
                            if objName is not None:
                                self.update_obj(str(objName),countOffset + addCount,setPoint,1.3)
    
    def collect_obj(self,defName):
        n = self.rootChildField.getCount()
        self.objIDlist = []
        self.objInfo = {}
        for i in reversed(range(n)):
            tempnode = self.rootChildField.getMFNode(i)
            if defName in tempnode.getDef():
                # import to list
                self.objIDlist.append(int(tempnode.getField("name").getSFString()))
                self.objInfo[tempnode] = {"Def":tempnode.getDef(),"Name":tempnode.getField("name").getSFString(),"Index":i}
                
    def add_obj(self,defName:str,count:int,setPoint:list,height:float,addPosition:int):
        rotation = random.uniform(-math.pi,math.pi)
        if self.configData["Tracking_Object"] == "Pedestrian":
            pointNum = random.randint(2,4)# random points
            trajectoryStr = "--trajectory="
            for i in range(pointNum):
                if i == pointNum-1:
                    trajectoryStr = trajectoryStr + str(round(setPoint[0]+random.uniform(-30,30),3)) + " " + str(round(setPoint[1]+random.uniform(-30,30),3))
                else:
                    trajectoryStr = trajectoryStr + str(round(setPoint[0]+random.uniform(-30,30),3)) + " " + str(round(setPoint[1]+random.uniform(-30,30),3)) + ","
            speedStr = "--speed=2"
            protoString = 'DEF ' + defName + str(count) + ' ' + self.configData["Tracking_Object"] + ' { translation ' + str(setPoint[0]) + ' ' + str(setPoint[1]) + ' ' + str(height) + ' rotation 0 0 1 '+ str(rotation) + ' name "' + str(count) + '"' + ' controllerArgs' + ' ["' + speedStr + '","' + trajectoryStr + '"]' + ' }'
        elif self.configData["Tracking_Object"] == "Hoap2":
            protoString = 'DEF ' + defName + str(count) + ' ' + self.configData["Tracking_Object"] + ' { translation ' + str(setPoint[0]) + ' ' + str(setPoint[1]) + ' ' + str(height) + ' rotation 0 0 1 '+ str(rotation) + ' name "' + str(count) + '"' + ' controllerArgs' + ' ["walk"]' + ' }'
        else:
            protoString = 'DEF ' + defName + str(count) + ' ' + self.configData["Tracking_Object"] + ' { translation ' + str(setPoint[0]) + ' ' + str(setPoint[1]) + ' ' + str(height) + ' rotation 0 0 1 '+ str(rotation) + ' name "' + str(count) + '"' + ' }'        
        self.rootChildField.importMFNodeFromString(addPosition,protoString)
        

        
    def update_obj(self,objName:str,count:int,setPoint:list,height:float):
        objNode,objDef,objIndex = self.getObjInfoByName(objName)
        trList = [setPoint[0],setPoint[1],height]
        roList = [0,0,1,random.uniform(-math.pi,math.pi)]
        objNode.getField('translation').setSFVec3f(trList)
        objNode.getField('rotation').setSFRotation(roList)
        objNode.getField('name').setSFString(str(count))
        objNode.restartController()
        objNode.resetPhysics()
        # if self.configData["Tracking_Object"] == "Pedestrian":
        #     pointNum = random.randint(2,4)# random points
        #     trajectoryStr = "--trajectory="
        #     for i in range(pointNum):
        #         if i == pointNum-1:
        #             trajectoryStr = trajectoryStr + str(round(setPoint[0]+random.uniform(-30,30),3)) + " " + str(round(setPoint[1]+random.uniform(-30,30),3))
        #         else:
        #             trajectoryStr = trajectoryStr + str(round(setPoint[0]+random.uniform(-30,30),3)) + " " + str(round(setPoint[1]+random.uniform(-30,30),3)) + ","
        #     speedStr = "--speed=2"
        #     objNode.getField('controllerArgs').setMFString(0,speedStr)
        #     objNode.getField('controllerArgs').setMFString(1,trajectoryStr)

        
    
    def getObjInfoByName(self,name):
        objNode = None
        objDef = None
        objIndex = None
        
        for obj in iter(self.objInfo):
            if name == self.objInfo[obj]["Name"]:
                objNode = obj
                objDef = self.objInfo[obj]["Def"]
                objIndex = self.objInfo[obj]["Index"]
        return objNode, objDef, objIndex
        
