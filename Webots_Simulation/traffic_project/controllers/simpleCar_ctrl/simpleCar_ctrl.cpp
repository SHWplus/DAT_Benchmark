// File:          simpleCar_ctrl.cpp
// Date:
// Description:
// Author:
// Modifications:

// You may need to add webots include files such as
// <webots/DistanceSensor.hpp>, <webots/Motor.hpp>, etc.
// and/or to add some other includes
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <webots/Gyro.hpp>
#include <webots/GPS.hpp>
#include <webots/InertialUnit.hpp>
#include <webots/Camera.hpp>
#include <Eigen/Eigen>
#include <webots/Keyboard.hpp>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include <string>
#include <random>
#include <../../libraries/myLibs/ALGoutfile.h>
#include <webots/Accelerometer.hpp>
#include <webots/Lidar.hpp>
#include "../drone_ctrl2/json_config_handle.h"
#include <sstream>
#include "../god_controller/Reward_Generator.h"
#include "../drone_ctrl2/joy_control.h"
#include "../drone_ctrl2/gimbal_control.h"
using namespace webots;
using namespace Eigen;
using namespace std;

#define STATE_PERIOD_MS 2
#define CLAMP(value, low, high) ((value) < (low) ? (low) : ((value) > (high) ? (high) : (value)))

int main(int argc, char **argv) {
  Supervisor *robot = new Supervisor();
  int timeStep = (int)robot->getBasicTimeStep();

  // read json config file
  configHandle config("../../config/env_config.json");
  // get description
  string simpleCarDef = robot->getSelf()->getDef();
  // sensor
  Camera *camera = robot->getCamera("camera");
  camera->enable(timeStep);
  GPS *gps = robot->getGPS("gps");
  gps->enable(timeStep);
  Accelerometer *acc = robot->getAccelerometer("accelerometer");
  acc->enable(timeStep);
  Gyro *gyro = robot->getGyro("gyro");
  gyro->enable(timeStep);
  InertialUnit *imu = robot->getInertialUnit("inertial unit");
  imu->enable(timeStep);
  Keyboard *keyboard = robot->getKeyboard();
  keyboard->enable(timeStep);
  Emitter *emitter = robot->getEmitter("emitter");
  Receiver *receiver = robot->getReceiver("receiver");
  receiver->enable(timeStep);

  // lidar init
  Lidar *lidar;
  if (config.get()->lidarEnable)
  {
    lidar = robot->getLidar("RPlidar A2");
    lidar->enable(timeStep);
    lidar->enablePointCloud();
  }

  JoyControl jCtrl((double)STATE_PERIOD_MS * 0.001);
  if (config.get()->simulationMode == string("demo"))
  {
    jCtrl.setMode(1);
  }
  else if (config.get()->simulationMode == string("train"))
  {
    jCtrl.setMode(2);
  }
  GimbalControl gCtrl((double)STATE_PERIOD_MS * 0.001);
  double c_data[6] = {-1.7,1.7,-1,1.5,-1.7,1.7};
  gCtrl.updateConstrain(c_data); 
  usrPublic::Odometry state = {};
  usrPublic::vector3 gimbal_angle = {};
  usrPublic::vector3 gimbal_cmd = {};
  double action[5] = {0}; // rl action data buff
  double step_count = 0;
  bool is_video_warmUp = false;
  int random_number = -1;
  bool is_nan = false;  dataDisplay<6> dispData(disp);
  rewardGenerator rewardG(robot, config.get()->rewardConfig.distanceScale, config.get()->rewardConfig.distanceRange, config.get()->rewardConfig.viewScale, config.get()->rewardConfig.viewRange);

  
  while (robot->step(timeStep) != -1) {
    double t = robot->getTime();
    // get sensor data
    const double *gps_data;
    const double *imu_data_Q;
    const double *imu_data_A;
    const double *gyro_data;
    const double *acc_data;

    gps_data = gps->getValues();
    imu_data_Q = imu->getQuaternion();
    imu_data_A = imu->getRollPitchYaw();
    gyro_data = gyro->getValues();
    acc_data = acc->getValues();
    double x = gps_data[0];
    double y = gps_data[1];
    double z = gps_data[2];
    static double prev_x = x;
    static double prev_y = y;
    static double prev_z = z;
    double vx = (x - prev_x) * 1e3 / STATE_PERIOD_MS;
    double vy = (y - prev_y) * 1e3 / STATE_PERIOD_MS;
    double vz = (z - prev_z) * 1e3 / STATE_PERIOD_MS;
    prev_x = x;
    prev_y = y;
    prev_z = z;

    Quaterniond q = Quaterniond(imu_data_Q[3], imu_data_Q[0], imu_data_Q[1], imu_data_Q[2]);

    state.position.x = x;
    state.position.y = y;
    state.position.z = z;
    state.orientation.x = q.x();
    state.orientation.y = q.y();
    state.orientation.z = q.z();
    state.orientation.w = q.w();
    state.angle.x = imu_data_A[0];
    state.angle.y = imu_data_A[1];
    state.angle.z = imu_data_A[2];
    state.linear.x = vx;
    state.linear.y = vy;
    state.linear.z = vz;
    state.angular.x = gyro_data[0];
    state.angular.y = gyro_data[1];
    state.angular.z = gyro_data[2];
    state.acc.x = acc_data[0];
    state.acc.y = acc_data[1];
    state.acc.z = acc_data[2];

    const LidarPoint *lidar_cloud;
    int lidar_number_of_points;
    int lidar_number_of_layers;
    if (config.get()->lidarEnable)
    {
      lidar_cloud = lidar->getLayerPointCloud(0);
      lidar_number_of_points = lidar->getNumberOfPoints();
      lidar_number_of_layers = lidar->getNumberOfLayers();
      // std::cout<<lidar_number_of_points<<std::endl;
    }

    usrPublic::Joy simpleCar_cmd = {};
    if (config.get()->simulationMode == string("demo"))
    {
      int key = keyboard->getKey();
      while (key > 0)
      {
        switch (key)
        {
          case keyboard->UP:
            simpleCar_cmd.axes[3] = 20;
            break;
          case keyboard->DOWN:
            simpleCar_cmd.axes[3] = -20;
            break;
          case keyboard->RIGHT:
            simpleCar_cmd.axes[0] = -90;
            break;
          case keyboard->LEFT:
            simpleCar_cmd.axes[0] = 90;
            break;
          case (keyboard->SHIFT + keyboard->RIGHT):
            simpleCar_cmd.axes[2] = -20;
            break;
          case (keyboard->SHIFT + keyboard->LEFT):
            simpleCar_cmd.axes[2] = 20;
            break;
          case (keyboard->SHIFT + keyboard->UP):
            simpleCar_cmd.axes[1] = 0.01;
            break;
          case (keyboard->SHIFT + keyboard->DOWN):
            simpleCar_cmd.axes[1] = -0.01;
            break;
          case 'W':
            gimbal_cmd.y -= 0.003;
            gimbal_cmd.y = CLAMP(gimbal_cmd.y, -1, 1);
            break;
          case 'S':
            gimbal_cmd.y += 0.003;
            gimbal_cmd.y = CLAMP(gimbal_cmd.y, -1, 1);
            break;
          case 'A':
            gimbal_cmd.z += 0.005;
            gimbal_cmd.z = CLAMP(gimbal_cmd.z, -1.7, 1.7);
            break;
          case 'D':
            gimbal_cmd.z -= 0.005;
            gimbal_cmd.z = CLAMP(gimbal_cmd.z, -1.7, 1.7);
            break;
        }
        key = keyboard->getKey();
      }
    }
    // get gimbal pose
    if(config.get()->simulationMode == string("train") || config.get()->simulationMode == string("video"))
    {
      string pitchAngle = Txt_Input("../../cache/" + simpleCarDef + "_PitchAngle.txt");
      if (pitchAngle == string("error"))
      {
        gimbal_cmd.y = 1.;
      }
      else
      {
        try
        {
          gimbal_cmd.y = std::stod(pitchAngle);
        }
        catch (const std::exception &e)
        {
          std::cerr << "Error: " << e.what() << std::endl;
          gimbal_cmd.y = 1.;
        }
      }
      gimbal_cmd.y = CLAMP(gimbal_cmd.y, 0.5, 1.5);
    }
    // action
    if (config.get()->simulationMode == string("train"))
    {
      
      // get action
      Txt_Input("../../cache/" + simpleCarDef + "_Global2Ctrl.txt", action, 5);
      if (t < 0.1)
      {
        // figure action
        simpleCar_cmd.axes[3] = 0;
        simpleCar_cmd.axes[2] = 0;
        simpleCar_cmd.axes[1] = 0;
        simpleCar_cmd.axes[0] = 0;
        step_count = action[4];
      }
      else
      {
        // figure action
        simpleCar_cmd.axes[3] = action[0];
        simpleCar_cmd.axes[2] = action[1];
        simpleCar_cmd.axes[1] = action[2];
        simpleCar_cmd.axes[0] = action[3] / M_PI * 180.;
        step_count = action[4];
      }
      if(config.get()->verbose == true)
      {
        std::cout << "id: " << simpleCarDef
                << "  ACTIONS  "
                << "  forward:" << std::setprecision(3) << simpleCar_cmd.axes[0]
                << "  leftRight:" << std::setprecision(3) << simpleCar_cmd.axes[1]
                << "  turn:" << std::setprecision(3) << simpleCar_cmd.axes[3] 
                << std::endl;
      }
    }
    else if(config.get()->simulationMode == string("video"))
    {
      static int countMax = int(1000. / 2. / config.get()->controlFreq);
      static double last_step_count = 0;
      if (countMax < 1)
      {
        countMax = 1;
      }
      if(step_count <= config.get()->video.warmUpSteps)
      {
        is_video_warmUp = false;
      }
      else
      {
        is_video_warmUp = true;
      }
      if(config.get()->video.randomAction == true && rewardG.carDef != string("ORIGIN"))
      {
        // use ctrl frequency
        if((step_count == 1) || ((step_count - last_step_count) >= countMax))
        {

          std::random_device rd;  
          std::mt19937 gen(rd());  

          std::uniform_int_distribution<> distrib(0, 5);
          random_number = distrib(gen);
          last_step_count = step_count;
        }
        // use random number to select random actions
        switch(random_number)
        {
          case 0: simpleCar_cmd.axes[3] = config.get()->video.forwardSpeed;
            break;
          case 1: simpleCar_cmd.axes[3] = config.get()->video.backwardSpeed;
            break;
          case 2: simpleCar_cmd.axes[2] = config.get()->video.leftSpeed;
            break;
          case 3: simpleCar_cmd.axes[2] = config.get()->video.rightSpeed;
            break;
          case 4: simpleCar_cmd.axes[0] = config.get()->video.cwOmega  / M_PI * 180.;
            break;
          case 5: simpleCar_cmd.axes[0] = config.get()->video.ccwOmega  / M_PI * 180.;
            break;
          case 6:
            break;
          default:
            break;
        }
        // video mode self count
        if(rewardG.carDef != string("ORIGIN"))
        {
          step_count++;
        }
      }
    }

    // TODO:get reward?
    rewardG.locateCamera(camera->getWidth(), camera->getHeight(), camera->getFov());
    if (config.get()->simulationMode == string("demo"))
    {
      rewardG.setTrackingCar("ORIGIN");
    }
    else if (config.get()->simulationMode == string("train") || config.get()->simulationMode == string("video"))
    {
      rewardG.updateTrackingCar();
    }
    if(t > 0.1)
    {
      // state.reward = rewardG.getReward(config.get()->simulationMode, config.get()->rewardConfig.rewardMode, config.get()->rewardConfig.rewardType, 0, 0);
      state.reward = 1;// force to be 1
    }
    // TODO：simpleCar control
    jCtrl.joyCb(simpleCar_cmd);
    jCtrl.stateCb(state);
    gCtrl.stateCb(state, gimbal_angle);
    gCtrl.cmdCb(gimbal_cmd);
    robot->getSelf()->getField("rollAngle")->setSFFloat(gCtrl.gbl2ctrl.axes[3]);
    robot->getSelf()->getField("pitchAngle")->setSFFloat(gCtrl.gbl2ctrl.axes[4]);
    robot->getSelf()->getField("yawAngle")->setSFFloat(gCtrl.gbl2ctrl.axes[5]);
    if (config.get()->simulationMode == string("train") || config.get()->simulationMode == string("video"))
    {
      static bool alreadyDone = false;
      // Update done status based on tracked vehicles
      // Update the done state according to the training execution step
      if (config.get()->simulationMode == string("video"))
      {
        state.done = (rewardG.isTrackingCarDisp == 2) ? 1 : 0;
      }
      else
      {
        state.done = 0;
      }
      string machineState;
      if (config.get()->simulationMode == string("train"))
      {
        machineState = Txt_Input("../../cache/" + simpleCarDef + "_MachineState.txt");
        static int noRewardCount = 0;
        if (state.reward > 0.001)
        {
          noRewardCount = 0;
        }
        else
        {
          noRewardCount++;
        }
        if (noRewardCount > config.get()->noRewardDoneSteps)
        {
          state.done = 1;
        }
      }
      if (step_count >= config.get()->trainTotalStep)
      {
        state.done = 1;
      }
      if (step_count < double(config.get()->initNoDoneSteps) && config.get()->simulationMode == string("train"))
      {
        state.done = 0;
      }

      if(is_nan == true)
      {
        state.done = 1;
      }

      if (config.get()->simulationMode == string("video"))
      {
        if (state.done == 1 && t > 0.7)
        {
          alreadyDone = true;
        }
        if (alreadyDone == true)
        {
          state.done = 1;
        }
      }
      if(config.get()->verbose == true)
      {
        std::cout << "id: " << simpleCarDef
                << "  done: " << state.done
                << "  reward: " << state.reward
                << "  count: " << step_count
                << "  time:" << std::setprecision(3) << t
                << "  carDir:" << rewardG.makeReward.carDir
                << "  pitchAngle:" << std::setprecision(3) << gimbal_cmd.y << std::endl;
      }
      // If using supervisor control mode, then move the drone directly to the target location
      if ((config.get()->simulationMode != string("video") || config.get()->video.randomAction == true) && jCtrl.initialized == true && state.done == 0 && machineState == string("2"))
      {
        const double tr_t[3] = {jCtrl.cmd_pos_(0), jCtrl.cmd_pos_(1), jCtrl.cmd_pos_(2)};
        double cmd_yaw = jCtrl.cmd_yaw_;
        while (cmd_yaw > M_PI)
        {
          cmd_yaw -= 2. * M_PI;
        }
        while (cmd_yaw < -M_PI)
        {
          cmd_yaw += 2. * M_PI;
        }
        const double ro_t[4] = {0, 0, 1, cmd_yaw};
        robot->getSelf()->getField("translation")->setSFVec3f(tr_t);
        robot->getSelf()->getField("rotation")->setSFRotation(ro_t);
      }
      else if(config.get()->simulationMode == string("video") && config.get()->video.randomAction == true && step_count>5 && step_count<(config.get()->trainTotalStep-5))
      {
        const double tr_t[3] = {jCtrl.cmd_pos_(0), jCtrl.cmd_pos_(1), jCtrl.cmd_pos_(2)};
        double cmd_yaw = jCtrl.cmd_yaw_;
        while (cmd_yaw > M_PI)
        {
          cmd_yaw -= 2. * M_PI;
        }
        while (cmd_yaw < -M_PI)
        {
          cmd_yaw += 2. * M_PI;
        }
        const double ro_t[4] = {0, 0, 1, cmd_yaw};
        robot->getSelf()->getField("translation")->setSFVec3f(tr_t);
        robot->getSelf()->getField("rotation")->setSFRotation(ro_t);
      }
      // send state,reward,done
      state.t = step_count;
      double state_list[22] = {};
      static double state_list_last[22] = {0};
      memcpy(state_list, &state, sizeof(state));
      for(int i=0;i<22;i++)
      {
        if(std::isnan(state_list[i])){
          is_nan = true;
        }
      }
      file_create("../../cache/" + simpleCarDef + "_Ctrl2Global.txt", ios::out);
      if(is_nan == false)
      {
        Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2Global.txt", ios::app, state_list, 22);
      }
      else
      {
        Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2Global.txt", ios::app, state_list_last, 22);
      }
      while (get_file_size("../../cache/" + simpleCarDef + "_Ctrl2Global.txt") < 22)
      {
        delete_file("../../cache/" + simpleCarDef + "_Ctrl2Global.txt");
        if(is_nan == false)
        {
          Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2Global.txt", ios::app, state_list, 22);
        }
        else
        {
          Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2Global.txt", ios::app, state_list_last, 22);
        }
      }
      if(is_nan == false)
      {
        memcpy(state_list_last, &state_list, sizeof(state_list));
      }

      if (config.get()->customizedReward)
      {
        double makeReward_list[51] = {};
        memcpy(makeReward_list, &rewardG.makeReward, sizeof(rewardG.makeReward) - sizeof(rewardG.makeReward.carTypename));
        for(int i=0;i<51;i++)
        {
          if(std::isnan(state_list[i])){
            is_nan = true;
          }
        }
        file_create("../../cache/" + simpleCarDef + "_Ctrl2GlobalR.txt", ios::out);
        if(is_nan == false)
        {
          Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2GlobalR.txt", ios::app, makeReward_list, 51, rewardG.makeReward.carTypename);
        }
        while (get_file_size("../../cache/" + simpleCarDef + "_Ctrl2GlobalR.txt") < 51)
        {
          delete_file("../../cache/" + simpleCarDef + "_Ctrl2GlobalR.txt");
          if(is_nan == false)
          {
            Txt_Output("../../cache/" + simpleCarDef + "_Ctrl2GlobalR.txt", ios::app, makeReward_list, 51, rewardG.makeReward.carTypename);
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("demo"))
    {
      std::cout << "reward: " << state.reward << std::endl;
      Node *droneNode = robot->getFromDef(rewardG.droneDef);
      const double tr_t[3] = {jCtrl.cmd_pos_(0), jCtrl.cmd_pos_(1), jCtrl.cmd_pos_(2)};
      double cmd_yaw = jCtrl.cmd_yaw_;
      while (cmd_yaw > M_PI)
      {
        cmd_yaw -= 2. * M_PI;
      }
      while (cmd_yaw < -M_PI)
      {
        cmd_yaw += 2. * M_PI;
      }
      const double ro_t[4] = {0, 0, 1, cmd_yaw};
      droneNode->getField("translation")->setSFVec3f(tr_t);
      droneNode->getField("rotation")->setSFRotation(ro_t);
    }
    jCtrl.setInitialized(true);

    // lidar and camera
    if (config.get()->simulationMode == string("demo"))
    {
      if ((int)(t * 1000) % (STATE_PERIOD_MS * 10) == 0 && is_nan == false)
      {
        string filename = "../../cache/" + simpleCarDef + "_VideoFrame.jpeg";
        camera->saveImage(filename, 100);
        if (config.get()->lidarEnable)
        {
          float cloudData[sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers / sizeof(float)] = {};
          memcpy(cloudData, lidar_cloud, sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers);
          file_create("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::out);
          Txt_Output("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          while (get_file_size("../../cache/" + simpleCarDef + "_LidarCloud.txt") < (sizeof(cloudData) / sizeof(float)))
          {
            delete_file("../../cache/" + simpleCarDef + "_LidarCloud.txt");
            Txt_Output("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("train"))
    {
      if ((int)(t * 1000) % (STATE_PERIOD_MS) == 0 && is_nan == false)
      {
        string filename = "../../cache/" + simpleCarDef + "_VideoFrame.jpeg";
        camera->saveImage(filename, 100);
        if (config.get()->lidarEnable)
        {
          float cloudData[sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers / sizeof(float)];
          memcpy(cloudData, lidar_cloud, sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers);
          file_create("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::out);
          // std::cout<<"point_cloud_size: "<<sizeof(cloudData)/sizeof(float)<<std::endl;
          Txt_Output("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          while (get_file_size("../../cache/" + simpleCarDef + "_LidarCloud.txt") < (sizeof(cloudData) / sizeof(float)))
          {
            delete_file("../../cache/" + simpleCarDef + "_LidarCloud.txt");
            Txt_Output("../../cache/" + simpleCarDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("video"))
    {
      static double last_frame_t = config.get()->video.startTime;
      static uint32_t videoCount = 0;
      static string foldername = "../../Videos/" + simpleCarDef;
      static int32_t episode = -1;
      if (episode == -1)
      {
        while (std::filesystem::exists(foldername + "/episode" + std::to_string(episode + 1)))
        {
          episode++;
        }
      }
      if (t >= config.get()->video.startTime && t <= (config.get()->video.startTime + config.get()->video.totalTime) && is_video_warmUp == true)
      {
        if (videoCount == 0)
        {
          std::ostringstream oss;
          oss << std::setw(6) << std::setfill('0') << videoCount; 
          std::string formatted = oss.str();                      
          string filename = foldername + "/episode" + std::to_string(episode) + "/" + formatted + ".jpeg";
          camera->saveImage(filename, 100);
          string jsonpath = foldername + "/episode" + std::to_string(episode) + "/" + "mark.json";
          if(config.get()->video.outputCarDir == true)
          {
            config.writeJsonIncrement(jsonpath, formatted, rewardG.makeReward.carDir);
          }
          else
          {
            config.writeJsonIncrement(jsonpath, formatted, state.reward, double(random_number));
          }
          videoCount++;
        }
        else if ((t - last_frame_t) >= (1. / static_cast<double>(config.get()->video.fps)))
        {
          std::ostringstream oss;
          oss << std::setw(6) << std::setfill('0') << videoCount; 
          std::string formatted = oss.str();                      
          string filename = foldername + "/episode" + std::to_string(episode) + "/" + formatted + ".jpeg";
          camera->saveImage(filename, 100);
          string jsonpath = foldername + "/episode" + std::to_string(episode) + "/" + "mark.json";
          if(config.get()->video.outputCarDir == true)
          {
            config.writeJsonIncrement(jsonpath, formatted, rewardG.makeReward.carDir);
          }
          else
          {
            config.writeJsonIncrement(jsonpath, formatted, state.reward, double(random_number));
          }
          videoCount++;
          last_frame_t = t;
        }
      }
    }
    else
    {
    }

  };

  delete robot;
  return 0;
}
