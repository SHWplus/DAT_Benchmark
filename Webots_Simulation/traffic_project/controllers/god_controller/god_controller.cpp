// File:          god_controller.cpp
// Date:
// Description:
// Author:
// Modifications:

// You may need to add webots include files such as
// <webots/DistanceSensor.hpp>, <webots/Motor.hpp>, etc.
// and/or to add some other includes
#include <webots/Robot.hpp>
#include <webots/Supervisor.hpp>
#include <iostream>
#include <string>
#include <webots/Camera.hpp>
#include <webots/Field.hpp>
#include "Camera_Track_Check_Super.h"
#include <webots/Receiver.hpp>
#include <webots/Emitter.hpp>
#include <string>
#include <../../libraries/myLibs/ALGoutfile.h>

// All the webots classes are defined in the "webots" namespace
using namespace webots;
using namespace Eigen;

int main(int argc, char **argv) {
  // create the Robot instance.
  Supervisor *robot = new Supervisor();

  // get custom runMode
  std::string run_mode = robot->getCustomData();

  // Node *camera_node = robot->getFromDef("m100camera");

  Node *camera_slot_node = robot->getFromDef("M100")->getFromProtoDef("CAMERA_SLOT");
  Node *land_node = robot->getFromDef("land");

  Node *trackingCar = robot->getFromDef("ORIGIN");
  std::cout<<"trackingCar: "<<trackingCar<<std::endl;

  Receiver* receiver = robot->getReceiver("receiver");
  // std::cout<<"receiver: "<<receiver<<std::endl;

  Emitter* emitter = robot->getEmitter("emitterReward");

  camera2real Camera2real;
  for (int i = 0; i < 6;i++)
  {
    std::string ballprotoString = "DEF LocationBall" + std::to_string(i + 1) + " trajectary {translation " + std::to_string(0+i) + " " + std::to_string(0+i) + " " + std::to_string(0) + "}";
    std::cout << ballprotoString << std::endl;
    robot->getRoot()->getField("children")->importMFNodeFromString(-1, ballprotoString);
    std::cout << "ok" + std::to_string(i + 1) << std::endl;
  }

  // get the time step of the current world.
  int timeStep = (int)robot->getBasicTimeStep();

  receiver->enable(timeStep);

  // Main loop:
  // - perform simulation steps until Webots is stopping the controller
  while (robot->step(timeStep) != -1) {

    const double *T_land_of_camera = land_node->getPose(camera_slot_node);
    Matrix<double,3,4> T_land_of_camera_M;
    for (int i = 0; i < 12;i++)
    {
      T_land_of_camera_M(i/4,i%4) = T_land_of_camera[i];
    }

    const double *T_camera_of_land = camera_slot_node->getPose(land_node);
    Matrix<double,3,4> T_camera_of_land_M;
    for (int i = 0; i < 12;i++)
    {
      T_camera_of_land_M(i/4,i%4) = T_camera_of_land[i];
    }

    const double *T_land_of_world = land_node->getPose(robot->getRoot());
    Matrix<double,3,4> T_land_of_world_M;
    for (int i = 0; i < 12;i++)
    {
      T_land_of_world_M(i/4,i%4) = T_land_of_world[i];
    }
    // std::cout << "T_land_of_world_M\n"
              // << T_land_of_world_M << std::endl;

    receiver->setChannel(3);
    double data[5] = {};
    if(receiver->getQueueLength() > 0)
    {
      const void* message = receiver->getData();
      float* p = (float*)message;
      for(int i = 0; i < 5; i++)
      {
        data[i] = p[i];
        // std::cout<< i <<" "<<data[i]<<std::endl;
      }
      receiver->nextPacket();
    }
    // std::cout<<"positionx: "<<data[0]<<"  positiony: "<<data[1]<<std::endl;
    

    // The origin of the coordinate system is in the upper left corner of the image, noted as (0, 0)
    // The four corner points of the camera
    Vector3d locationMid = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(data[2] * 0.5, data[3] * 0.5), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
    Vector3d locationLH = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(0, 0), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
    Vector3d locationLL = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(data[2], 0), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
    Vector3d locationRH = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(0, data[3]), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
    Vector3d locationRL = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(data[2], data[3]), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
    
    // Real-time update of tracked vehicle nodes
    string carDef = Txt_Input(string("../../cache/car.txt"));
    if(carDef != string("error")){
      Node* n = robot->getFromDef(carDef);
      if(n != NULL){
        trackingCar = n;
      }
    }
    // Get the coordinates of the assigned tracked vehicle in the world.
    const double *T_car_of_land = trackingCar->getPose(land_node);
    Vector3d V_car_of_land;
    for(int i = 0;i < 3;i++){
      V_car_of_land(i) = T_car_of_land[3 + i*4];
    }
    // std::cout<<"V_car_of_world: "<<V_car_of_land<<std::endl;

    float reward = 0;
    if(run_mode == std::string("local")){
      if(data[0] < 0 || data[1] < 0){
        reward = 0;
        // std::cout<<"is_tracking1: "<< reward <<std::endl;
      }
      else{
        // Coordinates of the target tracking
        Vector3d locationTar = Camera2real.Location_of_World_Calculate(Camera2real.Location_of_Camera_Calculate(Vector2d(data[0], data[1]), T_land_of_camera_M, data[4], Vector2d(data[3],data[2])), T_camera_of_land_M,T_land_of_world_M);
        reward = Camera2real.Get_Location_Reward(locationTar, locationMid, V_car_of_land, 4);
        // std::cout<<"is_tracking2: "<< reward <<std::endl;
      }
    }
    else if(run_mode == std::string("online")){
      reward = Camera2real.Get_Location_Reward(locationMid, V_car_of_land, 6);
    }
    // std::cout<<"reward: "<<reward<<std::endl;
    // emitter->setChannel(4);
    emitter->send(&reward,sizeof(reward));
    
    
    
    robot->getFromDef("LocationBall1")->getField("translation")->setSFVec3f(locationLH.data());
    robot->getFromDef("LocationBall2")->getField("translation")->setSFVec3f(locationLL.data());
    robot->getFromDef("LocationBall3")->getField("translation")->setSFVec3f(locationRH.data());
    robot->getFromDef("LocationBall4")->getField("translation")->setSFVec3f(locationRL.data());
    robot->getFromDef("LocationBall5")->getField("translation")->setSFVec3f(locationMid.data());
    // robot->getFromDef("LocationBall6")->getField("translation")->setSFVec3f(locationTar.data());
    

    // std::cout << "\033[2J";//terminal clearing
  };

  // Enter here exit cleanup code.

  delete robot;
  return 0;
}

