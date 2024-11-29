SIMULATION_MODE = ["demo", "video", "train"]
TRACKER_DEF = ["DRONE","CAR"]
TRACKING_OBJECT = ["SUMO_VEHICLE",
                   "Pedestrian",
                   "Shrimp",
                   "Create",
                   "Sojourner",
                   "Mantis",
                   "BB-8",
                   "AiboErs7",
                   "BioloidDog",
                   "FireBird6",
                   "Scout",
                   "GhostDog",
                   "Hoap2"
                   ]
REWARD_MODE = ["continuous","discrete"]
CAR_TYPE = ["passenger","bus","truck","trailer","motorcycle"]


SUMO_UPDATE = ["max_sumo_car",
               "fixed_car_group_num",
               "car_group_num",
               "car_import_interval",
               "car_type",
               "fixed_color",
               "normalize_color",
               "max_car_speed",
               "max_car_accel",
                "max_car_decel",
                "max_rou_distance",
                "min_rou_distance",
                "route_num",
                "fixed_seed",
                "random_seed"
                ]

def checkSumoUpdate(configData,configData_backup):
    configSumo = configData["Sumo_Params"]
    configSumoB = configData_backup["Sumo_Params"]
    for i in range(len(SUMO_UPDATE)):
        if configSumo[SUMO_UPDATE[i]] != configSumoB[SUMO_UPDATE[i]]:
            return True
    # if configData["Sumo_Params"]["fixed_car_group_num"] == False:
    #     return True
    return False

def check(input:str, container:list):
        is_contain = False
        for i in range(len(container)):
            if input == container[i]:
                is_contain = True
        if is_contain == True:
            return input
        else:
            return container[0]