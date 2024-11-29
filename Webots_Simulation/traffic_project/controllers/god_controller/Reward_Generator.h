#pragma once
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <iostream>
#include <string>
#include <webots/Camera.hpp>
#include <webots/Field.hpp>
#include <webots/Node.hpp>
#include "Camera_Track_Check_Super.h"
#include <../../libraries/myLibs/ALGoutfile.h>
#include "../drone_ctrl2/user_public.h"

using namespace webots;
using namespace std;

class rewardGenerator
{
public:
  rewardGenerator(Supervisor *_supervisor, double _distanceScale, double _distanceRange, double _viewScale, double _viewRange);
  ~rewardGenerator() {};
  void locateCamera(double _width, double _height, double _fov);
  void updateTrackingCar();
  void setTrackingCar(string _carDef);
  double getReward(string _trackingObj, string _run_mode, string _reward_mode, string _reward_type, double trackWidth = -1, double trackHeight = -1);
  void checkCarDirection(double stop_threshold, double turn_threshold);
  uint8_t isTrackingCarDisp = 0; 
  usrPublic::rewardData makeReward = {};
  string droneDef;
  string carDef = "ORIGIN";

private:
  camera2real Camera2real;
  Supervisor *supervisor;
  Node *trackingCar = nullptr;
  Node *land_node;
  Node *camera_slot_node;

  // camera five points
  Vector3d cameraMid;
  Vector3d cameraLH;
  Vector3d cameraLL;
  Vector3d cameraRH;
  Vector3d cameraRL;

  Matrix<double, 3, 4> T_land_of_camera_M;
  Matrix<double, 3, 4> T_camera_of_land_M;
  Matrix<double, 3, 4> T_land_of_world_M;

  double distanceScale = 0.05;
  double distanceRange = 7;
  double viewScale = 0.1;
  double viewRange = 1;

  std::vector<Eigen::Vector3d> pointContain;
};

/**
 * @description: construction function
 * @param {Supervisor} *_supervisor
 * @return {*}
 */
inline rewardGenerator::rewardGenerator(Supervisor *_supervisor, double _distanceScale, double _distanceRange, double _viewScale, double _viewRange)
{
  supervisor = _supervisor;

  droneDef = supervisor->getSelf()->getDef();
  camera_slot_node = supervisor->getSelf()->getFromProtoDef("CAMERA_SLOT");
  land_node = supervisor->getFromDef("land");
  trackingCar = supervisor->getFromDef("ORIGIN");

  // makeReward.Toyota.x = 4.2;
  // makeReward.Toyota.y = 1.8;
  // makeReward.Toyota.z = 1.4;

  // makeReward.Lincoln.x = 4.9;
  // makeReward.Lincoln.y = 1.8;
  // makeReward.Lincoln.z = 1.3;

  // makeReward.Tesla.x = 4.5;
  // makeReward.Tesla.y = 1.8;
  // makeReward.Tesla.z = 1.4;

  // makeReward.Rover.x = 4.5;
  // makeReward.Rover.y = 1.8;
  // makeReward.Rover.z = 1.55;

  // makeReward.BMW.x = 4.5;
  // makeReward.BMW.y = 1.8;
  // makeReward.BMW.z = 1.6;

  // makeReward.Citroen.x = 3.3;
  // makeReward.Citroen.y = 1.4;
  // makeReward.Citroen.z = 1.5;

  distanceScale = _distanceScale;
  distanceRange = _distanceRange;
  viewScale = _viewScale;
  viewRange = _viewRange;

  // For vehicle state recognition, first initialize a queue of length 3
  pointContain.emplace(pointContain.begin(), Eigen::Vector3d::Zero());
  pointContain.emplace(pointContain.begin(), Eigen::Vector3d::Zero());
  pointContain.emplace(pointContain.begin(), Eigen::Vector3d::Zero());
}

/**
 * @description: Calculate the coordinates of the four corner points of the camera as well as the center point
 * @param {double} _width
 * @param {double} _height
 * @param {double} _fov
 * @return {*}
 */
inline void rewardGenerator::locateCamera(double _width, double _height, double _fov)
{
  makeReward.cameraWidth = _width;
  makeReward.cameraHeight = _height;
  makeReward.cameraFov = _fov;

  const double *T_land_of_camera = land_node->getPose(camera_slot_node);
  for (int i = 0; i < 12; i++)
  {
    T_land_of_camera_M(i / 4, i % 4) = T_land_of_camera[i];
  }

  const double *T_camera_of_land = camera_slot_node->getPose(land_node);
  memcpy(&makeReward.T_ct, T_camera_of_land, sizeof(makeReward.T_ct));
  for (int i = 0; i < 12; i++)
  {
    T_camera_of_land_M(i / 4, i % 4) = T_camera_of_land[i];
  }

  const double *T_land_of_world = land_node->getPose(supervisor->getRoot());
  for (int i = 0; i < 12; i++)
  {
    T_land_of_world_M(i / 4, i % 4) = T_land_of_world[i];
  }
  cameraMid = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(_width * 0.5, _height * 0.5), T_land_of_camera_M, _fov, Vector2d(_height, _width)), T_camera_of_land_M, T_land_of_world_M);
  cameraLH = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(0.5 * (1 - viewRange) * _width, 0.5 * (1 - viewRange) * _height), T_land_of_camera_M, _fov, Vector2d(_height, _width)), T_camera_of_land_M, T_land_of_world_M);
  cameraLL = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(0.5 * (1 - viewRange) * _width, _height - 0.5 * (1 - viewRange) * _height), T_land_of_camera_M, _fov, Vector2d(_height, _width)), T_camera_of_land_M, T_land_of_world_M);
  cameraRH = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(_width - 0.5 * (1 - viewRange) * _width, 0.5 * (1 - viewRange) * _height), T_land_of_camera_M, _fov, Vector2d(_height, _width)), T_camera_of_land_M, T_land_of_world_M);
  cameraRL = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(_width - 0.5 * (1 - viewRange) * _width, _height - 0.5 * (1 - viewRange) * _height), T_land_of_camera_M, _fov, Vector2d(_height, _width)), T_camera_of_land_M, T_land_of_world_M);

  makeReward.cameraF = Camera2real.cameraF;
  makeReward.cameraMidPos.x = makeReward.T_ct[3];
  makeReward.cameraMidPos.y = makeReward.T_ct[7];
  makeReward.cameraMidPos.z = makeReward.T_ct[11];
}

/**
 * @description: update target car from file
 * @return {*}
 */
inline void rewardGenerator::updateTrackingCar()
{
  static string carName;
  string carData[2];
  // update target car node
  Txt_Input(string("../../cache/" + droneDef + "_Car.txt"), carData, 2);
  makeReward.carTypename = carData[1];
  if (carData[0] != string("error"))
  {
    Node *n = supervisor->getFromDef(carData[0]);
    if (n != NULL)
    {
      trackingCar = n;
      if (isTrackingCarDisp == 0)
      {
        carName = trackingCar->getField(string("name"))->getSFString();
      }
      isTrackingCarDisp = 1; // flag actuate
      if (isTrackingCarDisp == 1)
      {
        string newName = trackingCar->getField(string("name"))->getSFString();
        // std::cout<<"newName: "<<newName<<std::endl;
        if (newName != carName)
        {
          carName = newName;
          isTrackingCarDisp = 2; // flag finish
        }
      }
      else
      {
        isTrackingCarDisp = 0; // return init
      }
      carDef = string(carData[0]);
    }
    else
    {
      if (isTrackingCarDisp == 1)
      {
        isTrackingCarDisp = 2;
      }
      trackingCar = supervisor->getFromDef("ORIGIN");
      makeReward.carTypename = string("ToyotaPriusSimple");
      carDef = string("ORIGIN");
    }
  }
  if (trackingCar != nullptr)
  {
    checkCarDirection(0.001, 0.0001);
  }
}

inline void rewardGenerator::checkCarDirection(double stop_threshold, double turn_threshold)
{
  static Eigen::Vector4d lastRotation = Eigen::Vector4d::Zero();
  static Eigen::Vector3d lastTransform = Eigen::Vector3d::Zero();
  const double *tr = trackingCar->getField("translation")->getSFVec3f();
  const double *ro = trackingCar->getField("rotation")->getSFRotation();
  Eigen::Vector3d p(tr[0], tr[1], tr[2]);
  Eigen::Vector4d r(ro[0], ro[1], ro[2], ro[3]);
  double err = -(r(3) - lastRotation(3));
  lastRotation = r;
  // Dealing with positive and negative cycles
  if (err > M_PI)
  {
    err = err - 2 * M_PI;
  }
  else if (err < -M_PI)
  {
    err = 2 * M_PI + err;
  }
  // double dist = sqrt(pow(pointContain[0](1) - pointContain[1](1), 2) + pow(pointContain[0](0) - pointContain[1](0), 2));
  double dist = sqrt(pow(p(1) - lastTransform(1), 2) + pow(p(0) - lastTransform(0), 2));
  lastTransform = p;
  if (err > abs(turn_threshold))
  {
    makeReward.carDir = 2; // left
  }
  else if (err < -abs(turn_threshold))
  {
    makeReward.carDir = 3; // right
  }
  else
  {
    if (dist < abs(stop_threshold))
    {
      makeReward.carDir = 0; // stop
    }
    else
    {
      makeReward.carDir = 1; // straight
    }
  }
}

/**
 * @description: set tracking car
 * @param {string} _carDef
 * @return {*}
 */
inline void rewardGenerator::setTrackingCar(string _carDef)
{
  trackingCar = supervisor->getFromDef(_carDef);
}

/**
 * @description: get rewards
 * @param {string} _run_mode
 * @param {double} trackWidth
 * @param {double} trackHeight
 * @return {*}
 */
inline double rewardGenerator::getReward(string _trackingObj, string _run_mode, string _reward_mode, string _reward_type, double trackWidth, double trackHeight)
{
  // Get the coordinates of the assigned tracked vehicle in the world.
  const double *T_car_of_land = trackingCar->getPose(land_node);
  double T_car_of_land_temp[16];
  memcpy(T_car_of_land_temp, T_car_of_land, sizeof(T_car_of_land_temp));
  Vector3d V_car_comp(-1, 0, 0);
  if (_run_mode == string("demo"))
  {
    V_car_comp << 1, 0, 0;
  }
  if (_trackingObj != string("SUMO_VEHICLE"))
  {
    V_car_comp << 0, 0, 0;
  }
  Matrix3d M_car_of_land;
  Vector3d V_car_of_land;
  for (int i = 0; i < 3; i++)
  {
    V_car_of_land(i) = T_car_of_land[3 + i * 4];
    for (int j = 0; j < 3; j++)
    {
      M_car_of_land(i, j) = T_car_of_land[j + i * 4];
    }
  }
  V_car_of_land = V_car_of_land + M_car_of_land * V_car_comp;
  for (int i = 0; i < 3; i++)
  {
    T_car_of_land_temp[3 + i * 4] = V_car_of_land(i);
  }
  memcpy(&makeReward.T_tw, T_car_of_land_temp, sizeof(makeReward.T_tw));
  // Directly add the coordinates of the point at which the reward is calculated to the parameter
  makeReward.cameraMidGlobalPos.x = cameraMid(0);
  makeReward.cameraMidGlobalPos.y = cameraMid(1);
  makeReward.cameraMidGlobalPos.z = cameraMid(2);
  makeReward.carMidGlobalPos.x = V_car_of_land(0);
  makeReward.carMidGlobalPos.y = V_car_of_land(1);
  makeReward.carMidGlobalPos.z = V_car_of_land(2);
  // Get the coordinates and rotation angle of the vehicle with respect to the unoccupied vehicle.
  static Vector3d last_carDronePos = Vector3d::Zero();
  static double carDroneVel[3] = {0,0,0};
  static double last_carDroneVel[3] = {0,0,0};
  static double carDroneAcc[3] = {0,0,0};
  static double last_t = 0;
  const double *T_car_of_drone = trackingCar->getPose(supervisor->getFromDef(droneDef));
  Vector3d V_car_of_drone;
  Matrix3d M_car_of_drone;
  for (int i = 0; i < 3; i++)
  {
    V_car_of_drone(i) = T_car_of_drone[3 + i * 4];
    for (int j = 0; j < 3; j++)
    {
      M_car_of_drone(i, j) = T_car_of_drone[j + i * 4];
    }
  }
  V_car_of_drone = V_car_of_drone + M_car_of_drone * V_car_comp;
  makeReward.carDronePosOri.x = V_car_of_drone(0);
  makeReward.carDronePosOri.y = V_car_of_drone(1);
  makeReward.carDronePosOri.z = V_car_of_drone(2);
  double t_step = this->supervisor->getTime() - last_t;
  for(int i(0);i < 3;i++)
  {
    carDroneVel[i] = (V_car_of_drone(i) - last_carDronePos(i)) / t_step;
    carDroneAcc[i] = (carDroneVel[i] - last_carDroneVel[i]) / t_step;
  }
  memcpy(&makeReward.carDroneVel,carDroneVel,sizeof(carDroneVel));
  memcpy(&makeReward.carDroneAcc,carDroneAcc,sizeof(carDroneAcc));
  const double *Car_Ori = trackingCar->getField("rotation")->getSFRotation();
  const double *Drone_Ori = supervisor->getFromDef(droneDef)->getField("rotation")->getSFRotation();
  makeReward.carDronePosOri.w = Car_Ori[2] * Car_Ori[3] - Drone_Ori[2] * Drone_Ori[3];
  // makeReward.carDronePosOri.w = atan2(makeReward.carDronePosOri.y,makeReward.carDronePosOri.x);
  while (makeReward.carDronePosOri.w > M_PI)
  {
    makeReward.carDronePosOri.w -= 2 * M_PI;
  }
  while (makeReward.carDronePosOri.w < -M_PI)
  {
    makeReward.carDronePosOri.w += 2 * M_PI;
  }
  memcpy(last_carDroneVel,carDroneVel,sizeof(last_carDroneVel));
  last_carDronePos = V_car_of_drone;
  last_t = this->supervisor->getTime();

  double reward = 0;
  // std::cout << "cameraMid:  x:" << cameraMid(0) << "  y:" << cameraMid(1) << "  z:" << cameraMid(2) << std::endl;
  // std::cout << "car:        x:" << V_car_of_land(0) << "  y:" << V_car_of_land(1) << "  z:" << V_car_of_land(2) << std::endl;
  if (_run_mode == string("demo"))
  {
    // if(trackWidth < 0 || trackHeight < 0){
    //   reward = 0;
    //   // std::cout<<"is_tracking1: "<< reward <<std::endl;
    // }
    // else{
    //   // Coordinates of the target tracking
    //   Vector3d locationTar = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(trackWidth, trackHeight), T_land_of_camera_M, makeReward.cameraFov, Vector2d(makeReward.cameraHeight,makeReward.cameraWidth)), T_camera_of_land_M,T_land_of_world_M);
    //   reward = Camera2real.Get_Location_Reward(locationTar, cameraMid, V_car_of_land, distanceRange, distanceScale);
    //   // std::cout<<"is_tracking2: "<< reward <<std::endl;
    // }
    if (_reward_mode == string("discrete"))
    {
      if (_reward_type == string("distance"))
      {
        reward = Camera2real.Get_Location_Reward(cameraMid, V_car_of_land, distanceRange);
      }
      else if (_reward_type == string("view"))
      {
        Vector3d follow[5] = {cameraMid, cameraLH, cameraLL, cameraRL, cameraRH};
        reward = Camera2real.Get_View_Reward(follow, V_car_of_land);
      }
    }
    else if (_reward_mode == string("continuous"))
    {
      if (_reward_type == string("distance"))
      {
        reward = Camera2real.Get_Location_Reward(cameraMid, V_car_of_land, distanceRange, distanceScale);
      }
      else if (_reward_type == string("view"))
      {
        Vector3d follow[5] = {cameraMid, cameraLH, cameraLL, cameraRL, cameraRH};
        reward = Camera2real.Get_View_Reward(follow, V_car_of_land, viewScale);
      }
    }
  }
  else if (_run_mode == string("train") || _run_mode == string("video"))
  {
    if (_reward_mode == string("discrete"))
    {
      if (_reward_type == string("distance"))
      {
        reward = Camera2real.Get_Location_Reward(cameraMid, V_car_of_land, distanceRange);
      }
      else if (_reward_type == string("view"))
      {
        Vector3d follow[5] = {cameraMid, cameraLH, cameraLL, cameraRL, cameraRH};
        reward = Camera2real.Get_View_Reward(follow, V_car_of_land);
      }
    }
    else if (_reward_mode == string("continuous"))
    {
      if (_reward_type == string("distance"))
      {
        reward = Camera2real.Get_Location_Reward(cameraMid, V_car_of_land, distanceRange, distanceScale);
      }
      else if (_reward_type == string("view"))
      {
        Vector3d follow[5] = {cameraMid, cameraLH, cameraLL, cameraRL, cameraRH};
        reward = Camera2real.Get_View_Reward(follow, V_car_of_land, viewScale);
      }
    }
  }
  return reward;
}