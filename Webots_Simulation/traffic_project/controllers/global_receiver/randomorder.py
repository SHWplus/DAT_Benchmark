from lxml import etree
import random
import os
import sys

# get file root
def read_xml(file_path):
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()
    return tree, root

def display_xml(root):
    print(etree.tostring(root, pretty_print=True, encoding='unicode'))

def modify_xml(root, tag, index_attribute, index_attribute_value, attribute, new_value:list):
    count = 0
    for elem in root.iter(tag):
        elem.set(attribute, new_value[count])
        count=count+1

# Traversing elements and attributes from the root node
def collect_xml(root,tag,attribute):
    count=-1
    attribute_list=[]
    for elem in root.iter(tag):
        count=count+1
        attribute_list.append(elem.get(attribute))
    return count,attribute_list

def write_xml(tree, file_path):
    with open(file_path, 'wb') as file:
        tree.write(file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def groupAndSetDepart(root, totalNum:int, numPerGroup:int, intervalBetweenGroup:float, numByList:list=[], departList:list=[]):
    numlist=[]
    departlist=[]
    count = 0
    index = 0
    # print(totalNum)
    if(numPerGroup == 0):
        assert sum(numByList)<=totalNum, "sum of numByList must less than or equal to totalNum"
        if(sum(numByList)<=totalNum):
            numlist = numByList[:] + [1]*(totalNum-sum(numByList))
    else:
        remainder=totalNum%numPerGroup
        if(remainder != 0):
            numlist = [numPerGroup]* (totalNum//numPerGroup)+[remainder]
        else:
            numlist = [numPerGroup]* (totalNum//numPerGroup)


    # print("original numlist:",numlist)
    
    for i in range(len(numlist)):
        if(i==0):
            continue
        numlist[i]=numlist[i]+numlist[i-1]
    # print("numlist:",numlist)

    if(intervalBetweenGroup == 0):
        if(len(departList)<=len(numlist)):
            departlist = departList[:]
            for i in range(len(numlist)-len(departList)):
                departlist = departlist+[departlist[-1]+1]
        elif(len(departList)>len(numlist)):
            departlist = departList[:len(numlist)]
    else:
        for i in range(len(numlist)):
            departlist.append(0+i*intervalBetweenGroup)
    # print("departlist:",departlist)

    for elem in root.iter("vehicle"):
        # departAttr = elem.get("depart")
        elem.set("depart",str(departlist[index]))
        # print("depart",str(departlist[index]),count)
        count = count+1
        if(count>=numlist[index]):
            index=index+1
            
def random_by_os(folder_path, _sys, _configData):
    net_path = folder_path + '/sumo.net.xml'
    trip_path = folder_path + '/sumo.trip.xml'
    rou_path = folder_path + '/sumo.rou.xml'
    maxD = str(_configData["max_rou_distance"])
    minD = str(_configData["min_rou_distance"])
    rouN = str(_configData["route_num"])
    # Use the python path obtained from the system
    if _sys == "Linux":
        if _configData["fixed_seed"] == True:
            os.system(sys.executable + ' $SUMO_HOME/tools/randomTrips.py -n ' + net_path + ' -o ' + trip_path + ' --min-distance=' + minD + ' --max-distance=' + maxD + ' --end=' + rouN + ' --seed=' + str(_configData["random_seed"]) + ' --allow-fringe')
        else:
            os.system(sys.executable + ' $SUMO_HOME/tools/randomTrips.py -n ' + net_path + ' -o ' + trip_path + ' --min-distance=' + minD + ' --max-distance=' + maxD + ' --end=' + rouN + ' --random' + ' --allow-fringe')
    elif _sys == "Windows":
        if _configData["fixed_seed"] == True:
            os.system(sys.executable + ' %SUMO_HOME%/tools/randomTrips.py -n ' + net_path + ' -o ' + trip_path + ' --min-distance=' + minD + ' --max-distance=' + maxD + ' --end=' + rouN + ' --seed=' + str(_configData["random_seed"]) + ' --allow-fringe')       
        else:
            os.system(sys.executable + ' %SUMO_HOME%/tools/randomTrips.py -n ' + net_path + ' -o ' + trip_path + ' --min-distance=' + minD + ' --max-distance=' + maxD + ' --end=' + rouN + ' --random' + ' --allow-fringe')               
    # Python soft links created with webots
    # os.system('python3.11 $SUMO_HOME/tools/randomTrips.py -n ' + net_path + ' -o ' + trip_path + ' --min-distance ' + minD + ' --max-distance ' + maxD + ' --end ' + rouN + ' --seed ' + randS + ' --random')
    if _sys == "Linux":
        os.system('$SUMO_HOME/bin/duarouter --trip-files ' + trip_path + ' --net-file ' + net_path + ' --output-file ' + rou_path + ' --ignore-errors true')
    elif _sys == "Windows":
        os.system('%SUMO_HOME%/bin/duarouter --trip-files ' + trip_path + ' --net-file ' + net_path + ' --output-file ' + rou_path + ' --ignore-errors true')



# Insert description of vehicle speed
def add_speed_constrain(root, config):
    car_type=etree.Element('vType')
    car_type.set('id', 'type1')
    car_type.set('maxSpeed', str(config["max_car_speed"]))
    car_type.set('accel', str(config["max_car_accel"]))
    car_type.set('decel', str(config["max_car_decel"]))
    car_type.set('vClass', str(config["car_type"]))

    
    root.insert(0, car_type)
    root.insert(1, etree.Comment('\n '))  # Using comments to add line breaks
    
    # Find all vehicle elements
    for vehicle in root.findall('.//vehicle'):
        vehicle.set('type', 'type1')
    
        
def sumo_rou_random(folder_path, _numPerGroup, _configData):
    tree, root = read_xml(folder_path + '/sumo.rou.xml')

    count,attribute_list = collect_xml(root=root,tag="route",attribute="edges")
    random.shuffle(attribute_list)

    for i in range(count+1):
        modify_xml(root=root,tag="route",index_attribute="id",index_attribute_value=i.__str__(),attribute="edges",new_value=attribute_list)
    
    groupAndSetDepart(root=root,totalNum=count+1,numPerGroup=_numPerGroup,intervalBetweenGroup=_configData["car_import_interval"])
    
    write_xml(tree, folder_path + '/sumo.rou.xml')
    
def sumo_rou_random_os(folder_path, _numPerGroup, _sys, _configData):
    if _configData["rou_update"] == True:
        random_by_os(folder_path, _sys, _configData)
        
        tree, root = read_xml(folder_path + '/sumo.rou.xml')
        add_speed_constrain(root=root, config=_configData)
        count,attribute_list = collect_xml(root=root,tag="route",attribute="edges")
        
        groupAndSetDepart(root=root,totalNum=count+1,numPerGroup=_numPerGroup,intervalBetweenGroup=_configData["car_import_interval"])
        write_xml(tree, folder_path + '/sumo.rou.xml')




if __name__ == "__main__":
    
    file_path = '~/Documents/WebotsPro/webots_autodriving_drone/traffic_project_bridge/worlds/la3clean_net/sumo.rou.xml'
    tree, root = read_xml(file_path)

    count,attribute_list = collect_xml(root=root,tag="route",attribute="edges")
    random.shuffle(attribute_list)

    for i in range(count+1):
        # print(attribute_list[i])
        modify_xml(root=root,tag="route",index_attribute="id",index_attribute_value=i.__str__(),attribute="edges",new_value=attribute_list)

    # same group scale, same interval of depart, e.g. 180 car per group. The first group's depart is 0.0 and the second group's depart is 5.0, the third one is 10.0
    groupAndSetDepart(root=root,totalNum=count+1,numPerGroup=180,intervalBetweenGroup=5.)

    # customize group scale and intervals using list, the totalNum of this example is 3600
    gourplist=[600,1200,1800]
    departlist=[0.0,12.0,16.5]
    groupAndSetDepart(root=root,totalNum=count+1,numPerGroup=0,intervalBetweenGroup=0,numByList=gourplist,departList=departlist)

    
    write_xml(tree, file_path)
