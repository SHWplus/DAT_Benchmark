#pragma once

#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <Eigen/Eigen>
#include "user_public.h"
#include <webots/Accelerometer.hpp>
#include <type_traits>

using json = nlohmann::json;
using namespace webots;
using namespace Eigen;

typedef struct _configData_s{
    std::string simulationMode = "demo";
    bool droneSupervisorCtrl = false;
    int trainTotalStep = 2000;
    int initNoDoneSteps = 100;
    int noRewardDoneSteps = 1000;
    bool customizedReward = false;
    double controlFreq = 10;
    bool lidarEnable = false;
    bool cameraEnable = true;
    std::string trackingObject = "SUMO_VEHICLE";
    bool verbose = false;
    struct _droneRange{
        double maxHeight = 50;
        double minHeight = 1;
        double velocity = 30;
        double omiga = 6.283;
        double roll = 1.22;
        double pitch = 1.22;
        double distanceError = 20;
    };
    _droneRange droneRange;
    struct _rewardConfig{
        std::string rewardType = "view";
        std::string rewardMode = "continuous";
        double rewardCurOff = 0.001;
        double distanceScale = 0.05;
        double distanceRange = 7;
        double viewScale = 2;
        double viewRange = 1;
    };
    _rewardConfig rewardConfig;
    // struct _droneRandomConfig{
    //     bool viewPitchRandom = false;
    //     double viewPitchFixed = -1.2;viewScale
    //     double viewPitchRandomMax = -1.57;
    //     double viewPitchRandomMin = -0.7;
    // };
    // _droneRandomConfig droneRandomConfig;
    struct _outVideo{
        double fps = 30;
        double startTime = 0;
        double totalTime = 5;
        int warmUpSteps = 0;
        bool outputCarDir = true;
        bool randomAction = false;
        double forwardSpeed = 0;
        double backwardSpeed = 0;
        double leftSpeed = 0;
        double rightSpeed = 0;
        double cwOmega = 0;
        double ccwOmega = 0;
    };
    _outVideo video;
}configData_s;

std::string simMode[3] = {std::string("demo"),std::string("video"),std::string("train")};
std::string rType[2] = {std::string("distance"),std::string("view")};
std::string rMode[2] = {std::string("discrete"),std::string("continuous")};

void checkType(const auto& variable) {
    std::cout << "The type is: " << typeid(variable).name() << std::endl;
}

template<typename T>
bool checkIfString(T)
{
    if (std::is_same<T, std::string>::value)
    {
        return true;
    }
    else
    {
        return false;
    }
}

template<typename T>
bool checkIfBool(T)
{
    if (std::is_same<T, bool>::value)
    {
        return true;
    }
    else
    {
        return false;
    }
}

template<typename T>
bool checkIfInt(T)
{
    if (std::is_integral<T>::value)
    {
        return true;
    }
    else
    {
        return false;
    }
}

template<typename T>
bool checkIfFloat(T)
{
    if (std::is_floating_point<T>::value)
    {
        return true;
    }
    else
    {
        return false;
    }
}

class configHandle{
public:
    configHandle(std::string _filepath);
    ~configHandle(){}
    const configData_s *get(){ return &configData; }
    nlohmann::json read_json_file(const std::string& file_path);
    void write_json_file(const std::string& file_path, const nlohmann::json& json_obj);;
    void writeJsonIncrement(std::string& _filepath, std::string _mark, int _value);
    void writeJsonIncrement(std::string& _filepath, std::string _mark, double _reward,double _action);
private:
    std::string filepath;//json file path and name
    configData_s configData;//json file parse data
    bool safetyCheck(std::string obj,std::string* safeGroup,int num);
    
};


configHandle::configHandle(std::string _filepath):filepath(_filepath){
    std::ifstream ifs(filepath);
    if (!ifs.is_open()) {
        std::cerr << "Error opening json file\n";
        return;
    }
    
    json config;
    try {
        ifs >> config;
    } catch (const std::exception& e) {
        std::cerr << "Error parsing json file: " << e.what() << "\n";
        return;
    }
    ifs.close();// close it in case of memory leak

    if(this->safetyCheck(config.at("Simulation_Mode"),simMode,3))
    {
        configData.simulationMode = config.at("Simulation_Mode");
    }
    else
    {
        std::cerr << "Simulation mode(string) is not available!('demo','video','train')" 
                    << "    Use default value 'demo'." << std::endl;
    }
    configData.droneSupervisorCtrl = config.at("Drone_Supervisor_Ctrl");
    configData.trainTotalStep = config.at("Train_Total_Steps");
    configData.initNoDoneSteps = config.at("Init_No_Done_Steps");
    configData.noRewardDoneSteps = config.at("No_Reward_Done_Steps");
    configData.controlFreq = config.at("Control_Frequence");
    configData.customizedReward = config.at("Customized_Rewards");
    configData.lidarEnable = config.at("Lidar_Enable");
    configData.trackingObject = config.at("Tracking_Object");
    configData.verbose = config.at("Verbose");

    configData.droneRange.maxHeight = config.at("Done_Range").at("max_height");
    configData.droneRange.minHeight = config.at("Done_Range").at("min_height");
    configData.droneRange.velocity = config.at("Done_Range").at("velocity");
    configData.droneRange.omiga = config.at("Done_Range").at("omiga");
    configData.droneRange.roll = config.at("Done_Range").at("roll");
    configData.droneRange.pitch = config.at("Done_Range").at("pitch");
    configData.droneRange.distanceError = config.at("Done_Range").at("distance_error");

    if(this->safetyCheck(config.at("Reward_Config").at("reward_type"),rType,2))
    {
        configData.rewardConfig.rewardType = config.at("Reward_Config").at("reward_type");
    }
    else
    {
        std::cerr << "Reward type(string) is not available!('distance','view')" 
                    << "    Use default value 'view'." << std::endl;
    }
    if(this->safetyCheck(config.at("Reward_Config").at("reward_mode"),rMode,2))
    {
        configData.rewardConfig.rewardMode = config.at("Reward_Config").at("reward_mode");
    }
    else
    {
        std::cerr << "Reward mode(string) is not available!('discrete','continuous')" 
                    << "    Use default value 'continuous'." << std::endl;
    }
    configData.rewardConfig.rewardCurOff = config.at("Reward_Config").at("reward_cut_off");
    configData.rewardConfig.distanceScale = config.at("Reward_Config").at("distance_scale");
    configData.rewardConfig.distanceRange = config.at("Reward_Config").at("distance_range");
    configData.rewardConfig.viewScale = config.at("Reward_Config").at("view_scale");
    configData.rewardConfig.viewRange = config.at("Reward_Config").at("view_range");

    configData.video.fps = config.at("Out_Video").at("fps");
    configData.video.startTime = config.at("Out_Video").at("start_time");
    configData.video.totalTime = config.at("Out_Video").at("total_time");
    configData.video.warmUpSteps = config.at("Out_Video").at("warm_up_steps");
    configData.video.outputCarDir = config.at("Out_Video").at("output_car_dir");
    configData.video.randomAction = config.at("Out_Video").at("random_action");
    configData.video.forwardSpeed = config.at("Out_Video").at("forward_speed");
    configData.video.backwardSpeed = config.at("Out_Video").at("backward_speed");
    configData.video.leftSpeed = config.at("Out_Video").at("left_speed");
    configData.video.rightSpeed = config.at("Out_Video").at("right_speed");
    configData.video.cwOmega = config.at("Out_Video").at(("cw_omega"));
    configData.video.ccwOmega = config.at("Out_Video").at("ccw_omega");

    // if(configData.verbose == true)
    // {
    //     std::cout<< " \n \n"<<std::endl;
    //     std::cout<< "    Environment config successful!\n \n"<<std::endl;
    //     std::cout<< "    Simulation_Mode:       " << configData.simulationMode << std::endl;
    //     std::cout<< "    Drone_Supervisor_Ctrl: " << configData.droneSupervisorCtrl << std::endl;
    //     std::cout<< "    Train_Total_Steps:     " << configData.trainTotalStep << std::endl;
    //     std::cout<< "    Control_Frequence:     " << configData.controlFreq << std::endl;
    //     std::cout<< "    Customized_Rewards:    " << configData.customizedReward << std::endl;
    //     std::cout<< "    Lidar_Enable:          " << configData.lidarEnable << std::endl;
    //     std::cout<< "    Done_Range: {\n"
    //                 << "        max_height:      " << configData.droneRange.maxHeight << "\n"
    //                 << "        min_height:      " << configData.droneRange.minHeight << "\n"
    //                 << "        velocity:        " << configData.droneRange.velocity << "\n"
    //                 << "        omiga:           " << configData.droneRange.omiga << "\n"
    //                 << "        roll:            " << configData.droneRange.roll << "\n"
    //                 << "        pitch:           " << configData.droneRange.pitch << "\n"
    //                 << "        distance_error:  " << configData.droneRange.distanceError << std::endl;
    //     std::cout<< "    Reward_Config: {\n"
    //                 << "        reward_mode:     " << configData.rewardConfig.rewardMode << "\n"
    //                 << "        distance_scale:  " << configData.rewardConfig.distanceScale << "\n"
    //                 << "        reward_range:    " << configData.rewardConfig.rewardRange << std::endl;
    //     std::cout<< "    Out_Video: {\n"
    //                 << "        fps:             " << configData.video.fps << "\n"
    //                 << "        start_time:      " << configData.video.startTime << "\n"
    //                 << "        total_time:      " << configData.video.totalTime << "\n"
    //                 << "        output_car_dir:  " << configData.video.outputCarDir << "\n"
    //                 << "        random_action:   " << configData.video.randomAction << std::endl;
    //     std::cout<< "    }\n \n \n"<<std::endl;
    // }
    
}

// read JSON file
nlohmann::json configHandle::read_json_file(const std::string& file_path) {
    std::ifstream file(file_path);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        return nlohmann::json();
    }

    nlohmann::json json_obj;
    file >> json_obj;
    file.close();

    return json_obj;
}

// write JSON file
void configHandle::write_json_file(const std::string& file_path, const nlohmann::json& json_obj) {
    std::ofstream file(file_path);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        return;
    }

    file << json_obj.dump(4); // Formatting output using 4 space indentation
    file.close();
}


void configHandle::writeJsonIncrement(std::string& _filepath, std::string _mark, int _value)
{
    json object = read_json_file(_filepath);
    object[_mark] = _value;
    write_json_file(_filepath, object);
}

void configHandle::writeJsonIncrement(std::string& _filepath, std::string _mark, double _reward,double _action)
{
    json object = read_json_file(_filepath);
    double _value[2] = {_reward,_action};
    object[_mark] = _value;
    write_json_file(_filepath, object);
}

bool configHandle::safetyCheck(std::string obj,std::string* safeGroup,int num)
{
    for(int i(0);i<num;i++)
    {
        if(obj == safeGroup[i])
        {
            return true;
        }
    }
    return false;
}
