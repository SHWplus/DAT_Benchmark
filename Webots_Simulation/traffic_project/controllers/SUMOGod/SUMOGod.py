"""SUMOGod controller."""

from controller import Supervisor
from controller import Node
import random
import transforms3d as tfs
import numpy as np
import queue

class getSumoCarNode:
    '''
    description: randomly select a target sumo car
    param {*} self
    param {*} _sumoId: usually the same as drone id
    param {*} _usedSumoDefList: a list that record used target car
    param {*} _sumoDictionary: a list that record used dictionary
    param {*} _sumoGetFlag: a flag that record whether getting a car
    return {*}
    '''
    def __init__(self, _sumoId, _usedSumoDefList, _sumoDictionary, _sumoGetFlag, _randomSeed = None):
        self.sumoId = _sumoId
        self.usedSumoDefList = _usedSumoDefList # create a list, record sumo vehicles that is already allocated
        # self.usedSumoDefList = []
        self.sumoDictionary = _sumoDictionary
        self.sumoGetFlag = _sumoGetFlag
        self.carName = None
        self.currentUseCarNode = None
        self.transVector = None
        self.rotateAngle = None
        if _randomSeed != None:
            random.seed(_randomSeed)

    '''
    description: collect all sumo cars from root tree
    param {*} self
    param {Supervisor} supervisor: a supervisor
    param {str} usual_sumo_carname: joint feature name
    return {*}
    '''
    def CollectSumoCar(self, supervisor:Supervisor,usual_sumo_carname:str = "SUMO_VEHICLE"):
        '''collect all SUMO car nodes from world'''
        cardictionary={}
        rootnode=supervisor.getRoot()
        root_children_field=rootnode.getField("children")
        n=root_children_field.getCount()

        for i in reversed(range(n)):
            tempnode=root_children_field.getMFNode(i)
            if usual_sumo_carname in tempnode.getDef():
                # Node:{Def,Typename,color}
                if usual_sumo_carname == "SUMO_VEHICLE":   
                    cardictionary[tempnode]={"Def":tempnode.getDef(),"Name":tempnode.getField("name").getSFString(),"Typename":tempnode.getField("children").getMFNode(0).getTypeName()}
                else:
                    cardictionary[tempnode]={"Def":tempnode.getDef(),"Name":tempnode.getField("name").getSFString()}                    
                
        return cardictionary

    
    '''
    description: get all car typenames
    param {*} self
    param {dict} cardictionary
    param {bool} removeDuplicate
    return {*}
    '''
    def GetAllCarTypename(self, cardictionary:dict,removeDuplicate:bool=False):
        '''return a list of all sumo cars' names'''
        typename_list=[]

        for car in iter(cardictionary):
            typename_list.append(cardictionary[car]["Typename"])
        if removeDuplicate:
            typename_list=list(set(typename_list))

        return typename_list

    # '''
    # description: get all car colors
    # param {*} self
    # param {dict} cardictionary
    # param {bool} removeDuplicate
    # return {*}
    # '''
    # def GetAllCarRGB(self, cardictionary:dict,removeDuplicate:bool=False):
    #     '''return a list of all sumo cars' color'''
    #     RGB_list=[]

    #     for car in iter(cardictionary):
    #         RGB_list.append(cardictionary[car]["color"])
    #     if removeDuplicate:
    #         RGB_list=[list(t) for t in set(tuple(_) for _ in RGB_list)]

    #     return RGB_list
    
    '''
    description: get all car DEFs
    param {*} self
    param {dict} cardictionary
    param {bool} removeDuplicate
    return {*}
    '''
    def GetAllCarDef(self, cardictionary:dict,removeDuplicate:bool=False):
        '''return a list of all sumo cars' Def'''
        DEF_list=[]

        for car in iter(cardictionary):
            DEF_list.append(cardictionary[car]["Def"])
        if removeDuplicate:
            DEF_list=[list(t) for t in set(tuple(_) for _ in DEF_list)]

        return DEF_list
    
    '''
    description: get all car names
    param {*} self
    param {dict} cardictionary
    param {bool} removeDuplicate
    return {*}
    '''
    def GetAllCarName(self, cardictionary:dict,removeDuplicate:bool=False):
        '''return a list of all sumo cars' Def'''
        Name_list=[]

        for car in iter(cardictionary):
            Name_list.append(cardictionary[car]["Name"])
        if removeDuplicate:
            Name_list=[list(t) for t in set(tuple(_) for _ in Name_list)]

        return Name_list

    # '''
    # description: use typename and color to get car information
    # param {*} self
    # param {dict} cardictionary
    # param {str} carType
    # param {list} color
    # return {*}
    # '''
    # def GetCarInfoByTypeandRGB(self, cardictionary:dict, carType:str, color:list):
    #     '''find a sumo car by type and colorRGB\n
    #         return the first car found: 
    #             Webots Node,Def'''
    #     carNode:Node=None
    #     carDef:str=None
    #     translation:list=None

    #     for car in iter(cardictionary):
    #         if carType == cardictionary[car]["Typename"] and color == cardictionary[car]["color"]:
    #             carNode= car
    #             carDef=cardictionary[car]["Def"]
    #             carName=cardictionary[car]["Name"]
    #             carTypeName=cardictionary[car]["Typename"]
    #             break

    #     return carNode,carDef,carName,carTypeName
    
    '''
    description: use DEF to get car information
    param {*} self
    param {dict} cardictionary
    param {str} _carDef
    return {*}
    '''
    def GetCarInfoByDef(self, cardictionary:dict, _carDef:str):
        '''find a sumo car by def\n
            return the first car found: 
                Webots Node,Def'''
        carNode:Node=None
        carDef:str=None

        for car in iter(cardictionary):
            if _carDef == cardictionary[car]["Def"]:
                carNode= car
                carDef=cardictionary[car]["Def"]
                carName=cardictionary[car]["Name"]
                carTypeName=cardictionary[car]["Typename"]
                break
            
        return carNode,carDef,carName,carTypeName
    
    '''
    description: use car name to get car information
    param {*} self
    param {dict} cardictionary
    param {str} _carName
    return {*}
    '''
    def GetCarInfoByName(self, cardictionary:dict, _carName:str, _objName:str):
        '''find a sumo car by def\n
            return the first car found: 
                Webots Node,Def'''
        carNode:Node=None
        carDef:str=None
        carName:str=None
        carTypeName:str=None

        for car in iter(cardictionary):
            if _carName == cardictionary[car]["Name"]:
                carNode= car
                carDef=cardictionary[car]["Def"]
                carName=cardictionary[car]["Name"]
                if _objName == "SUMO_VEHICLE":
                    carTypeName=cardictionary[car]["Typename"]
                else:
                    carTypeName = _objName
                break
            
        return carNode,carDef,carName,carTypeName

    '''
    description: use supervisor to move a drone above the target car
    param {*} self
    param {Node} carNode
    param {Node} droneNode
    param {*} transVector
    return {*}
    '''
    def MoveDroneToCar(self, carNode:Node, droneNode:Node, transVector, rotateAngle, isReset:bool):
        '''move a drone to a car while the car is in the map
            return True or False'''
        try:
            carOr = carNode.getOrientation()
            carTr = carNode.getPosition()
            if carTr[0] < 5000:
                carOrV = carNode.getField('rotation').getSFRotation()
                carTrV = carNode.getField('translation').getSFVec3f()
                carOr = np.dot(np.reshape(carOr,(3,3)),tfs.euler.euler2mat(0,0,rotateAngle,"sxyz"))
                carTr = np.reshape(carTr,(3,1))
                droneTrSet = carTr + np.dot(carOr,np.array(transVector).reshape((3,1)))
                carOrV[3] = carOrV[3] + carOrV[2] * rotateAngle
                droneNode.getField('translation').setSFVec3f(list(droneTrSet))
                droneNode.getField('rotation').setSFRotation(carOrV)
                if isReset == True:
                    droneNode.resetPhysics()
                    droneNode.restartController()
                return True
            else:
                return False
        except:
            return False
            
    '''
    description: random target sumo car init that block the process until success
    param {*} self
    param {Supervisor} supervisor
    param {int} timeStep
    param {Node} droneNode
    param {*} transVector
    return {*} true or false
    '''
    def SingleProcessRandomInitBlock(self, supervisor:Supervisor, timeStep:int, droneNode:Node, transVector, rotateAngle, objName:str, fixedColorList=None):
        self.transVector = transVector
        self.rotateAngle = rotateAngle
        is_car_get = False
        while supervisor.step(timeStep) != -1:
            # collect info of all vehicles
            cardictionary = self.CollectSumoCar(supervisor,objName)
            # randomly choose one if get
            if cardictionary != {} and is_car_get == False:
                # get necessary list
                Name_list = self.GetAllCarName(cardictionary)
                # create a param list
                availableList = []
                for i in range(len(Name_list)):
                    flag = True
                    for j in reversed(self.usedSumoDefList):
                        if Name_list[i] == j:
                            flag = False
                            break
                    if flag == True:
                        availableList.append(i)
                if len(availableList) > 0:
                    # randomly sample an existed vehicle node
                    randomChoice = random.randint(1, len(availableList)) - 1
                    # already get vehicles
                    is_car_get = True
                    # get info of car
                    carNode,carDef,self.carName,carTypeName = self.GetCarInfoByName(cardictionary, Name_list[availableList[randomChoice]],objName)
                    self.currentUseCarNode = carNode
                    # put vehicles DEF in
                    self.usedSumoDefList.append(self.carName)
                    # change vehicle color
                    if fixedColorList is not None:
                        carNode.getField("children").getMFNode(0).getField("color").setSFVec3f(fixedColorList)
                
            
            if is_car_get == True:
                if self.MoveDroneToCar(carNode, droneNode, transVector, rotateAngle, True) == True:
                    with open("../../cache/" + droneNode.getDef() + "_Car.txt", "w") as f:
                        f.write(carDef + "\n" + carTypeName)
                    return True
        
    '''
    description: random target sumo car init which has no block
    param {*} self
    param {Supervisor} supervisor
    param {int} timeStep
    param {Node} droneNode
    param {*} transVector
    return {*} true or false
    '''
    def SingleProcessRandomInit(self, supervisor:Supervisor, timeStep:int, droneNode:Node, transVector, rotateAngle, objName:str, fixedColorList=None):
        '''no block version: single process random simulation init
            running until move a drone to a random car while the car is in the map
                return True or False'''
        self.transVector = transVector
        self.rotateAngle = rotateAngle
        is_car_get = False
        is_dict_get = False
        for i in range(len(self.sumoGetFlag)):
            if self.sumoGetFlag[i] == True:
                is_dict_get = True
        if is_dict_get == False:
            self.sumoDictionary = self.CollectSumoCar(supervisor,objName)
            self.sumoGetFlag[self.sumoId] = True
        if self.sumoDictionary != {} and is_car_get == False:
            Name_list = self.GetAllCarName(self.sumoDictionary)
            availableList = []
            for i in range(len(Name_list)):
                flag = True
                for j in reversed(self.usedSumoDefList):
                    if Name_list[i] == j:
                        flag = False
                        break
                if flag == True:
                    availableList.append(i)
            if len(availableList) > 0:
                randomChoice = random.randint(1, len(availableList)) - 1
                is_car_get = True
                carNode,carDef,self.carName,carTypeName = self.GetCarInfoByName(self.sumoDictionary, Name_list[availableList[randomChoice]],objName)
                self.currentUseCarNode = carNode
                self.usedSumoDefList.append(self.carName)
                if fixedColorList is not None:
                    carNode.getField("children").getMFNode(0).getField("color").setSFVec3f(fixedColorList)

        if is_car_get == True:
            with open("../../cache/" + droneNode.getDef() + "_Car.txt", "w") as f:
                f.write(carDef + "\n" + carTypeName)
            return self.MoveDroneToCar(carNode, droneNode, transVector, rotateAngle, True)
        else:
            with open("../../cache/" + droneNode.getDef() + "_Car.txt", "w") as f:
                f.write("error" + "\n" + "error")
            return False
        
    '''
    description: reset sumo dictionary
    param {*} self
    return {*}
    '''
    def ResetSumoDictionary(self):
        self.sumoGetFlag[self.sumoId] = False
        
    '''
    description: reset def record list
    param {*} self
    return {*}
    '''
    def delectDefList(self):
        self.usedSumoDefList.remove(self.carName)
                
            
