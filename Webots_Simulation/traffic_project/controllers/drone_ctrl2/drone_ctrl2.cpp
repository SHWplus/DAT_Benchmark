// File:          drone_ctrl2.cpp
// Date:
// Description:   this is a drone controller for M100 flight
// Author:
// Modifications:

// You may need to add webots include files such as
// <webots/DistanceSensor.hpp>, <webots/Motor.hpp>, etc.
// and/or to add some other includes
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <webots/Gyro.hpp>
#include <webots/GPS.hpp>
#include <webots/Motor.hpp>
#include <webots/InertialUnit.hpp>
#include <webots/LED.hpp>
#include <webots/Camera.hpp>
#include <webots/PositionSensor.hpp>
#include <Eigen/Eigen>
#include <webots/Keyboard.hpp>
#include <webots/Emitter.hpp>
#include <webots/Receiver.hpp>
#include "position_control.h"
#include "attitude_control.h"
#include "joy_control.h"
#include "gimbal_control.h"
#include <../../libraries/myLibs/SecondButterworthLPF.h>
#include "tracking_control.h"
#include <string>
#include <random>
#include <../../libraries/myLibs/ALGoutfile.h>
#include <../god_controller/Reward_Generator.h>
#include <webots/Accelerometer.hpp>
#include <webots/Lidar.hpp>
#include "json_config_handle.h"
#include <sstream>
#include "../god_controller/Reward_Generator.h"
#include <webots/Display.hpp>
// #define BOOST_NO_CXX11_SCOPED_ENUMS
// #include <boost/filesystem.hpp>
// #undef BOOST_NO_CXX11_SCOPED_ENUMS

// All the webots classes are defined in the "webots" namespace
using namespace webots;
using namespace Eigen;
using namespace std;

#define STATE_PERIOD_MS 2
#define MAX_MOTOR_VEL 10000
#define CLAMP(value, low, high) ((value) < (low) ? (low) : ((value) > (high) ? (high) : (value)))

bool is_nan = false;

void cmdCb(usrPublic::Joy msg, Motor *motor1, Motor *motor2, Motor *motor3, Motor *motor4)
{
  for (int i = 0; i < 4; i++)
  {
    if (std::isnan(msg.axes[i]))
    {
      is_nan = true;
    }
  }
  motor1->setVelocity(CLAMP(msg.axes[0], -MAX_MOTOR_VEL, MAX_MOTOR_VEL));
  motor2->setVelocity(CLAMP(msg.axes[1], -MAX_MOTOR_VEL, MAX_MOTOR_VEL));
  motor3->setVelocity(CLAMP(msg.axes[2], -MAX_MOTOR_VEL, MAX_MOTOR_VEL));
  motor4->setVelocity(CLAMP(msg.axes[3], -MAX_MOTOR_VEL, MAX_MOTOR_VEL));
}

void gcmdCb(usrPublic::Joy msg, Motor *motor1, Motor *motor2, Motor *motor3,bool _is_supervisor,Supervisor *_robot)
{
  if(_is_supervisor == true)
  {
    _robot->getSelf()->getField("rollAngle")->setSFFloat(msg.axes[3]);
    _robot->getSelf()->getField("pitchAngle")->setSFFloat(msg.axes[4]);
    _robot->getSelf()->getField("yawAngle")->setSFFloat(msg.axes[5]);
  }
  else
  {
    for (int i = 0; i < 3; i++)
    {
      if (std::isnan(msg.axes[i]))
      {
        is_nan = true;
      }
    }
    motor1->setTorque(CLAMP(msg.axes[0], -3, 3));
    motor2->setTorque(CLAMP(msg.axes[1], -3, 3));
    motor3->setTorque(CLAMP(msg.axes[2], -3, 3));
  }
}

void serialRec(Receiver *_receiver, float *buffer, int size)
{
  if (_receiver->getQueueLength() > 0)
  {
    const void *message = _receiver->getData();
    float *p = (float *)message;
    for (int i = 0; i < size; i++)
    {
      buffer[i] = p[i];
    }
    _receiver->nextPacket();
  }
}

int main(int argc, char **argv)
{
  // create the Robot instance.
  // Robot *robot = new Robot();
  Supervisor *robot = new Supervisor();

  // get the time step of the current world.
  int timeStep = (int)robot->getBasicTimeStep();

  // read json config file
  configHandle config("../../config/env_config.json");

  // get custom runMode
  string run_mode = robot->getCustomData();
  // get discription
  string droneDef = robot->getSelf()->getDef();
  // four motors
  Motor *motor1 = robot->getMotor("front_right_motor");
  Motor *motor2 = robot->getMotor("front_left_motor");
  Motor *motor3 = robot->getMotor("rear_left_motor");
  Motor *motor4 = robot->getMotor("rear_right_motor");
  motor1->setPosition(INFINITY);
  motor2->setPosition(INFINITY);
  motor3->setPosition(INFINITY);
  motor4->setPosition(INFINITY);
  motor1->setVelocity(0);
  motor2->setVelocity(0);
  motor3->setVelocity(0);
  motor4->setVelocity(0);
  // gimbal motors
  Motor *camera_roll_motor = robot->getMotor("camera roll");
  Motor *camera_pitch_motor = robot->getMotor("camera pitch");
  Motor *camera_yaw_motor = robot->getMotor("camera yaw");
  camera_roll_motor->setPosition(INFINITY);
  camera_pitch_motor->setPosition(INFINITY);
  camera_yaw_motor->setPosition(INFINITY);
  camera_roll_motor->setVelocity(0);
  camera_pitch_motor->setVelocity(0);
  camera_yaw_motor->setVelocity(0);
  // camera_roll_motor->setControlPID(Kroll,Iroll,Droll);
  // camera_pitch_motor->setControlPID(Kpitch,Ipitch,Dpitch);
  // camera_yaw_motor->setControlPID(Kyaw,Iyaw,Dyaw);
  // gimbal position sensor
  PositionSensor *camera_roll_sensor = robot->getPositionSensor("camera roll sensor");
  PositionSensor *camera_pitch_sensor = robot->getPositionSensor("camera pitch sensor");
  PositionSensor *camera_yaw_sensor = robot->getPositionSensor("camera yaw sensor");
  camera_roll_sensor->enable(timeStep);
  camera_pitch_sensor->enable(timeStep);
  camera_yaw_sensor->enable(timeStep);
  // sensors
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
  LED *led = robot->getLED("led");
  led->set(1);
  Keyboard *keyboard = robot->getKeyboard();
  keyboard->enable(timeStep);
  Emitter *emitter = robot->getEmitter("emitter");
  Receiver *receiver = robot->getReceiver("receiver");
  receiver->enable(timeStep);
  Display *disp = robot->getDisplay("display");

  // lidar init
  Lidar *lidar;
  if (config.get()->lidarEnable)
  {
    lidar = robot->getLidar("RPlidar A2");
    lidar->enable(timeStep);
    lidar->enablePointCloud();
  }

  // custom types
  PositionControl pCtrl;
  AttitudeControl aCtrl;
  JoyControl jCtrl((double)STATE_PERIOD_MS * 0.001);
  if (config.get()->simulationMode == string("demo"))
  {
    jCtrl.setMode(1);
  }
  else if (config.get()->simulationMode == string("train"))
  {
    jCtrl.setMode(2);
  }
  usrPublic::Odometry state = {};
  usrPublic::vector3 gimbal_angle = {};
  bool drone_fly = true;
  usrPublic::vector3 gimbal_cmd = {};
  GimbalControl gCtrl((double)STATE_PERIOD_MS * 0.001);
  float error[6] = {0}; // follow_anything data buff
  float last_error[4] = {0};
  int check_count[4] = {0};
  bool is_tracking = false;
  TrackingCtrl trackCtrl(timeStep);
  double action[5] = {0}; // rl action data buff
  double step_count = 0;
  rewardGenerator rewardG(robot, config.get()->rewardConfig.distanceScale, config.get()->rewardConfig.distanceRange, config.get()->rewardConfig.viewScale, config.get()->rewardConfig.viewRange);
  bool is_video_warmUp = false;
  int random_number = -1;
  double initParams[2] = {1.,0};

  // Main loop:
  // - perform simulation steps until Webots is stopping the controller
  while (robot->step(timeStep) != -1)
  {
    double t = robot->getTime();
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
    gimbal_angle.x = camera_roll_sensor->getValue();
    gimbal_angle.y = camera_pitch_sensor->getValue();
    gimbal_angle.z = camera_yaw_sensor->getValue();

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

    usrPublic::Joy fly_cmd = {}; // must be inited empty
    if (config.get()->simulationMode == string("demo"))
    {
      // 键盘控制
      int key = keyboard->getKey();
      while (key > 0)
      {
        switch (key)
        {
        case keyboard->UP:
          fly_cmd.axes[3] = 20;
          break;
        case keyboard->DOWN:
          fly_cmd.axes[3] = -20;
          break;
        case keyboard->RIGHT:
          fly_cmd.axes[0] = -90;
          break;
        case keyboard->LEFT:
          fly_cmd.axes[0] = 90;
          break;
        case (keyboard->SHIFT + keyboard->RIGHT):
          fly_cmd.axes[2] = -20;
          break;
        case (keyboard->SHIFT + keyboard->LEFT):
          fly_cmd.axes[2] = 20;
          break;
        case (keyboard->SHIFT + keyboard->UP):
          fly_cmd.axes[1] = 0.01;
          // fly_cmd.axes[1] = 3;
          // printf("target altitude: %f [m]\n", fly_cmd.axes[1]);
          break;
        case (keyboard->SHIFT + keyboard->DOWN):
          fly_cmd.axes[1] = -0.01;
          // fly_cmd.axes[1] = -2;
          // printf("target altitude: %f [m]\n", fly_cmd.axes[1]);
          break;
        case 'O':
          drone_fly = true;
          break;
        case 'W':
          gimbal_cmd.y -= 0.003;
          gimbal_cmd.y = CLAMP(gimbal_cmd.y, -0.5, 1.5);
          break;
        case 'S':
          gimbal_cmd.y += 0.003;
          gimbal_cmd.y = CLAMP(gimbal_cmd.y, -0.5, 1.5);
          break;
        case 'A':
          gimbal_cmd.z += 0.005;
          gimbal_cmd.z = CLAMP(gimbal_cmd.z, -1.7, 1.7);
          break;
        case 'D':
          gimbal_cmd.z -= 0.005;
          gimbal_cmd.z = CLAMP(gimbal_cmd.z, -1.7, 1.7);
          break;
        case 'U':
          is_tracking = true;
          break;
        case 'I':
          is_tracking = false;
          break;
        }
        key = keyboard->getKey();
      }
    }
    // get target gimbal pose and actions
    if (config.get()->simulationMode == string("train"))
    {
      drone_fly = true;
      // string pitchAngle = Txt_Input("../../cache/" + droneDef + "_PitchAngle.txt");
      // if (pitchAngle == string("error"))
      // {
      //   gimbal_cmd.y = 1.;
      // }
      // else
      // {
      //   try
      //   {
      //     gimbal_cmd.y = std::stod(pitchAngle);
      //   }
      //   catch (const std::exception &e)
      //   {
      //     std::cerr << "Error: " << e.what() << std::endl;
      //     gimbal_cmd.y = 1.;
      //   }
      // }
      Txt_Input("../../cache/" + droneDef + "_InitParams.txt", initParams, 2);
      gimbal_cmd.y = CLAMP(initParams[0], 0.5, 1.5);
      rewardG.makeReward.initDirection = initParams[1];
      // get actions
      Txt_Input("../../cache/" + droneDef + "_Global2Ctrl.txt", action, 5);
      if (t < 0.1)
      {
        // figure actions
        fly_cmd.axes[3] = 0;
        fly_cmd.axes[2] = 0;
        fly_cmd.axes[1] = 0;
        fly_cmd.axes[0] = 0;
        step_count = action[4];
      }
      else
      {
        // figure actions
        fly_cmd.axes[3] = action[0];
        fly_cmd.axes[2] = action[1];
        fly_cmd.axes[1] = action[2];
        fly_cmd.axes[0] = action[3] / M_PI * 180.;
        step_count = action[4];
      }
      // std::cout<<fly_cmd.axes[3]<<", "<<fly_cmd.axes[2]<<", "<<fly_cmd.axes[1]<<", "<<fly_cmd.axes[0]<<std::endl;
      if(config.get()->verbose == true)
      {
        std::cout << "id: " << droneDef
                << "  ACTIONS  "
                << "  forward:" << std::setprecision(3) << fly_cmd.axes[3]
                << "  leftRight:" << std::setprecision(3) << fly_cmd.axes[2]
                << "  turn:" << std::setprecision(3) << fly_cmd.axes[0] 
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
          // establish random engine
          std::random_device rd;  // get seed
          std::mt19937 gen(rd());  // random generator
          // create a uniform distribution
          std::uniform_int_distribution<> distrib(0, 5);
          random_number = distrib(gen);
          last_step_count = step_count;
        }
        // use random number to select random actions
        switch(random_number)
        {
          case 0: fly_cmd.axes[3] = config.get()->video.forwardSpeed;
            break;
          case 1: fly_cmd.axes[3] = config.get()->video.backwardSpeed;
            break;
          case 2: fly_cmd.axes[2] = config.get()->video.leftSpeed;
            break;
          case 3: fly_cmd.axes[2] = config.get()->video.rightSpeed;
            break;
          case 4: fly_cmd.axes[0] = config.get()->video.cwOmega  / M_PI * 180.;
            break;
          case 5: fly_cmd.axes[0] = config.get()->video.ccwOmega  / M_PI * 180.;
            break;
          case 6:
            break;
          default:
            break;
        }
        // std::cout << "id: " << droneDef
        //         << "  x: " << random_number
        //         << std::endl;
      }
    }

    if (config.get()->simulationMode == string("video"))
    {
      drone_fly = true;
      // string pitchAngle = Txt_Input("../../cache/" + droneDef + "_PitchAngle.txt");
      // if (pitchAngle == string("error"))
      // {
      //   gimbal_cmd.y = 1.;
      // }
      // else
      // {
      //   try
      //   {
      //     gimbal_cmd.y = std::stod(pitchAngle);
      //   }
      //   catch (const std::exception &e)
      //   {
      //     std::cerr << "Error: " << e.what() << std::endl;
      //     gimbal_cmd.y = 1.;
      //   }
      // }
      Txt_Input("../../cache/" + droneDef + "_InitParams.txt", initParams, 2);
      gimbal_cmd.y = CLAMP(initParams[0], 0.5, 1.5);
      rewardG.makeReward.initDirection = initParams[1];
      // video mode self count
      if(rewardG.carDef != string("ORIGIN"))
      {
        step_count++;
      }
    }

    if (config.get()->simulationMode == string("demo"))
    {
      // get follow_anything data
      receiver->setChannel(1);
      serialRec(receiver, error, 6);
      // figure follow params
      for (int i = 0; i < 4; i++)
      {
        if (is_tracking == false)
        {
          error[i] = 0;
        }
        if (error[i] == last_error[i])
        {
          check_count[i]++;
        }
        else
        {
          check_count[i] = 0;
        }
        if (check_count[i] > 500)
        {
          check_count[i] = 500;
        }
        if (check_count[i] > 70)
        {
          error[i] = 0;
          // is_tracking = false;
          // printf("no\n");
        }
        last_error[i] = error[i];
      }
    }
    // std::cout<< "positionx: "<< error[4] << " " << "positiony: " << error[5] << std::endl;
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
      state.reward = rewardG.getReward(config.get()->trackingObject, config.get()->simulationMode, config.get()->rewardConfig.rewardMode, config.get()->rewardConfig.rewardType, error[4], error[5]);
    }
    if (config.get()->simulationMode == string("demo"))
    {
      usrPublic::vector4 trackin = {};
      trackin.x = error[2];
      trackin.y = error[0];
      trackin.z = error[1];
      if (is_tracking == false)
      {
        trackin.w = 0;
      }
      else
      {
        trackin.w = gimbal_cmd.y; // fov compensation
      }
      trackCtrl.stateCb(state, gimbal_angle);
      trackCtrl.cmdCb(trackin);

      if (is_tracking)
      {
        fly_cmd.axes[3] = trackCtrl.track2joy.x;
        fly_cmd.axes[1] = trackCtrl.track2joy.z;
        fly_cmd.axes[2] = trackCtrl.track2joy.y; // int image_width = camera->getWidth();
      }
    }

    // 无人机控制
    jCtrl.joyCb(fly_cmd);
    jCtrl.stateCb(state);
    pCtrl.cmdCb(jCtrl.joy2pos);
    pCtrl.stateCb(state, config.get());
    aCtrl.cmdCb(pCtrl.pos2att);
    aCtrl.stateCb(state);
    gCtrl.stateCb(state, gimbal_angle);
    gCtrl.cmdCb(gimbal_cmd);
    if (drone_fly == true)
    {
      cmdCb(aCtrl.att2ctrl, motor1, motor2, motor3, motor4);
    }
    gcmdCb(gCtrl.gbl2ctrl, camera_roll_motor, camera_pitch_motor, camera_yaw_motor,config.get()->droneSupervisorCtrl,robot);

    rewardG.makeReward.trackerHeight = jCtrl.cmd_pos_(2);
    rewardG.makeReward.cameraPitch = gimbal_cmd.y;

    if (config.get()->simulationMode == string("train") || config.get()->simulationMode == string("video"))
    {
      static bool alreadyDone = false;
      // update done status based on tracked vehicles
      // update the done state according to the training execution step
      // if(state.done == 0){
      if (config.get()->simulationMode == string("video"))
      {
        state.done = (rewardG.isTrackingCarDisp == 2) ? 1 : 0;
      }
      else
      {
        state.done = (pCtrl.done) | ((rewardG.isTrackingCarDisp == 2) ? 1 : 0);
      }
      string machineState;
      if (config.get()->simulationMode == string("train"))
      {
        machineState = Txt_Input("../../cache/" + droneDef + "_MachineState.txt");
        static int noRewardCount = 0;
        if (state.reward > config.get()->rewardConfig.rewardCurOff)
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
      // }
      // else{
      //   state.done = 1;(
      // }

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
        std::cout << "id: " << droneDef
                << "  done: " << state.done
                << "  reward: " << state.reward
                << "  count: " << step_count
                << "  time:" << std::setprecision(3) << t
                << "  carDir:" << rewardG.makeReward.carDir
                << "  pitchAngle:" << std::setprecision(3) << gimbal_cmd.y
                << "  doneState:" << pCtrl.done_state << std::endl;
      } 
      // std::cout << "id: " << droneDef
      //           << "  x: " << rewardG.makeReward.carDronePosOri.x
      //           << "  y: " << rewardG.makeReward.carDronePosOri.y
      //           << "  z: " << rewardG.makeReward.carDronePosOri.z
      //           << "  w: " << rewardG.makeReward.carDronePosOri.w
      //           << std::endl;
      if(pCtrl.done_state == string("distance") || pCtrl.done_state == string("yaw velocity"))
      {
        rewardG.makeReward.crash = true;
      }
      else{
        rewardG.makeReward.crash = false;
      }
      // std::cout << "cmd_pos:" << jCtrl.cmd_pos_ << std::endl;
      // If using supervisor control mode, then move the drone directly to the target location
      if (config.get()->droneSupervisorCtrl == true && (config.get()->simulationMode != string("video") || config.get()->video.randomAction == true) && jCtrl.initialized == true && state.done == 0 && machineState == string("2"))
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
      file_create("../../cache/" + droneDef + "_Ctrl2Global.txt", ios::out);
      if(is_nan == false)
      {
        Txt_Output("../../cache/" + droneDef + "_Ctrl2Global.txt", ios::app, state_list, 22);
      }
      else
      {
        Txt_Output("../../cache/" + droneDef + "_Ctrl2Global.txt", ios::app, state_list_last, 22);
      }
      while (get_file_size("../../cache/" + droneDef + "_Ctrl2Global.txt") < 22)
      {
        delete_file("../../cache/" + droneDef + "_Ctrl2Global.txt");
        if(is_nan == false)
        {
          Txt_Output("../../cache/" + droneDef + "_Ctrl2Global.txt", ios::app, state_list, 22);
        }
        else
        {
          Txt_Output("../../cache/" + droneDef + "_Ctrl2Global.txt", ios::app, state_list_last, 22);
        }
      }
      if(is_nan == false)
      {
        memcpy(state_list_last, &state_list, sizeof(state_list));
      }

      
      if (config.get()->customizedReward)
      {
        double makeReward_list[60] = {};
        memcpy(makeReward_list, &rewardG.makeReward, sizeof(rewardG.makeReward) - sizeof(rewardG.makeReward.carTypename));
        for(int i=0;i<60;i++)
        {
          if(std::isnan(state_list[i])){
            is_nan = true;
          }
        }
        file_create("../../cache/" + droneDef + "_Ctrl2GlobalR.txt", ios::out);
        if(is_nan == false)
        {
          Txt_Output("../../cache/" + droneDef + "_Ctrl2GlobalR.txt", ios::app, makeReward_list, 60, rewardG.makeReward.carTypename);
        }
        while (get_file_size("../../cache/" + droneDef + "_Ctrl2GlobalR.txt") < 60)
        {
          delete_file("../../cache/" + droneDef + "_Ctrl2GlobalR.txt");
          if(is_nan == false)
          {
            Txt_Output("../../cache/" + droneDef + "_Ctrl2GlobalR.txt", ios::app, makeReward_list, 60, rewardG.makeReward.carTypename);
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("demo"))
    {
      // std::cout << "id: " << droneDef
      //           << "  x: " << rewardG.makeReward.carDronePosOri.x
      //           << "  y: " << rewardG.makeReward.carDronePosOri.y
      //           << "  z: " << rewardG.makeReward.carDronePosOri.z
      //           << "  w: " << rewardG.makeReward.carDronePosOri.w
      //           << "  reward: " << state.reward << std::endl;
      // std::cout << "id: " << droneDef
      //           << "  x: " << rewardG.cameraMid(0)
      //           << "  y: " << rewardG.makeReward.carDronePosOri.y
      //           << "  z: " << rewardG.makeReward.carDronePosOri.z
      //           << "  reward: " << state.reward << std::endl;
      std::cout << "reward: " << state.reward << std::endl;
      // double Ddata[6] = {rewardG.makeReward.carDroneVel.x,rewardG.makeReward.carDroneVel.y,rewardG.makeReward.carDroneVel.z,
      //                     rewardG.makeReward.carDroneAcc.x,rewardG.makeReward.carDroneAcc.y,rewardG.makeReward.carDroneAcc.z};
      // dispData.sendCtrl(Ddata);
      if (config.get()->droneSupervisorCtrl == true)
      {
        Node *droneNode = robot->getFromDef(rewardG.droneDef);
        const double tr_t[3] = {jCtrl.cmd_pos_(0), jCtrl.cmd_pos_(1), jCtrl.cmd_pos_(2)};
        double cmd_yaw = jCtrl.cmd_yaw_;
        // if (cmd_yaw > M_PI)
        // {
        //   cmd_yaw = cmd_yaw - 2. * M_PI * int((cmd_yaw + M_PI) / (2. * M_PI));
        // }
        // else if (cmd_yaw < -M_PI)
        // {
        //   cmd_yaw = cmd_yaw - 2. * M_PI * int((cmd_yaw - M_PI) / (2. * M_PI));
        // }
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
    }
    jCtrl.setInitialized(true);

    // Radar point cloud information and camera
    if (config.get()->simulationMode == string("demo"))
    {
      if ((int)(t * 1000) % (STATE_PERIOD_MS * 10) == 0 && is_nan == false)
      {
        string filename = "../../cache/" + droneDef + "_VideoFrame.jpeg";
        camera->saveImage(filename, 100);
        if (config.get()->lidarEnable)
        {
          float cloudData[sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers / sizeof(float)] = {};
          memcpy(cloudData, lidar_cloud, sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers);
          file_create("../../cache/" + droneDef + "_LidarCloud.txt", ios::out);
          Txt_Output("../../cache/" + droneDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          while (get_file_size("../../cache/" + droneDef + "_LidarCloud.txt") < (sizeof(cloudData) / sizeof(float)))
          {
            delete_file("../../cache/" + droneDef + "_LidarCloud.txt");
            Txt_Output("../../cache/" + droneDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("train"))
    {
      // if ((int)(t * 1000) % (250/int(config.get()->controlFreq)) == 0)
      if ((int)(t * 1000) % (STATE_PERIOD_MS) == 0 && is_nan == false)
      {
        string filename = "../../cache/" + droneDef + "_VideoFrame.jpeg";
        camera->saveImage(filename, 100);
        if (config.get()->lidarEnable)
        {
          float cloudData[sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers / sizeof(float)];
          memcpy(cloudData, lidar_cloud, sizeof(LidarPoint) * lidar_number_of_points * lidar_number_of_layers);
          file_create("../../cache/" + droneDef + "_LidarCloud.txt", ios::out);
          // std::cout<<"point_cloud_size: "<<sizeof(cloudData)/sizeof(float)<<std::endl;
          Txt_Output("../../cache/" + droneDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          while (get_file_size("../../cache/" + droneDef + "_LidarCloud.txt") < (sizeof(cloudData) / sizeof(float)))
          {
            delete_file("../../cache/" + droneDef + "_LidarCloud.txt");
            Txt_Output("../../cache/" + droneDef + "_LidarCloud.txt", ios::app, cloudData, sizeof(cloudData) / sizeof(float));
          }
        }
      }
    }
    else if (config.get()->simulationMode == string("video"))
    {
      static double last_frame_t = config.get()->video.startTime;
      static uint32_t videoCount = 0;
      static string foldername = "../../Videos/" + droneDef;
      static int32_t episode = -1;
      if (episode == -1)
      {
        while (std::filesystem::exists(foldername + "/episode" + std::to_string(episode + 1)))
        {
          episode++;
        }
      }
      // static boost::filesystem::path fn(foldername);
      if (t >= config.get()->video.startTime && t <= (config.get()->video.startTime + config.get()->video.totalTime) && is_video_warmUp == true)
      {
        if (videoCount == 0)
        {
          // // use boost
          // if (!boost::filesystem::is_directory(fn))
          // {
          //   std::cout << "begin create path: " << foldername << std::endl;
          //   if (!boost::filesystem::create_directory(fn))
          //   {
          //     std::cout << "create_directories failed: " << foldername << std::endl;
          //     return -1;
          //   }
          // }
          // else
          // {
          //   std::cout << foldername << " aleardy exist" << std::endl;
          // }
          // boost::filesystem::remove_all(fn);
          // std::cout << "clear directory: " << foldername << std::endl;
          std::ostringstream oss;
          oss << std::setw(6) << std::setfill('0') << videoCount; // Set the width to 6 and the fill character to '0'
          std::string formatted = oss.str();                      // Converting an output stream to a string
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
          oss << std::setw(6) << std::setfill('0') << videoCount; // Set the width to 6 and the fill character to '0'
          std::string formatted = oss.str();                      // Converting an output stream to a string
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

  // Enter here exit cleanup code.

  delete robot;
  return 0;
}
