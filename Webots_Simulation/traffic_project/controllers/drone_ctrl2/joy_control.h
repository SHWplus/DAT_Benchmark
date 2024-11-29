#pragma once
#include "user_public.h"
#include <Eigen/Eigen>
#include <../../libraries/myLibs/SecondButterworthLPF.h>
#include <string.h>

#define HEIGHT_OFFSET 1

class JoyControl
{
public:
  JoyControl(double _state_period);
  ~JoyControl();
  usrPublic::Joy joy2pos = {}; // control data sent to attitude_control.h
  void joyCb(usrPublic::Joy msg);
  void stateCb(usrPublic::Odometry msg);
  void setMode(uint8_t _mode){
    mode = _mode;
  }
  void setInitialized(bool _init)
  {
    initialized = _init;
  }
public:
  Eigen::Vector3d cmd_pos_;
  Eigen::Vector3d cmd_vel_b_;
  Eigen::Vector3d current_vel_b_;
  Eigen::Vector3d vel_b_;
  double cmd_yawrate_;
  double cmd_yaw_;
  double state_period;
  SecondOrderButterworthLPF tarF[4];
  uint8_t mode = 1;
  bool initialized = false;
};

JoyControl::JoyControl(double _state_period):state_period(_state_period)
{
  cmd_pos_ = Eigen::Vector3d::Zero();
  cmd_vel_b_ = Eigen::Vector3d::Zero();
  vel_b_ = Eigen::Vector3d::Zero();
  cmd_yaw_ = 0;
  cmd_yawrate_ = 0;
  // for(auto i : tarF)
  // {
  //   i.init(20, 1./state_period);
  // }
  for(int i=0;i<4;i++){
    tarF[i].init(20,1./state_period);
  }
}

JoyControl::~JoyControl() {}

void JoyControl::joyCb(usrPublic::Joy msg)
{
  cmd_vel_b_(0) = tarF[0].f(msg.axes[3]);
  cmd_vel_b_(1) = tarF[1].f(msg.axes[2]);
  // cmd_vel_b_(2) = tarF[2].f(msg.axes[1]);
  cmd_pos_(2) += msg.axes[1];
  cmd_yawrate_ = tarF[3].f(msg.axes[0] * M_PI / 180.0);
  // cmd_vel_b_(0) = msg.axes[3];
  // cmd_vel_b_(1) = msg.axes[2];
  // cmd_vel_b_(2) = msg.axes[1];
  // cmd_yawrate_ = msg.axes[0] * M_PI / 180.0;
}

void JoyControl::stateCb(usrPublic::Odometry msg)
{
  Eigen::Quaterniond q(msg.orientation.w,
                       msg.orientation.x,
                       msg.orientation.y,
                       msg.orientation.z);
  Eigen::Matrix3d R(q);
  
  Eigen::Vector3d b1c, b2c, b3c;
  Eigen::Vector3d b1 = R.col(0);
  b3c = Eigen::Vector3d::UnitZ();
  b2c = b3c.cross(b1).normalized();
  b1c = b2c.cross(b3c).normalized();
  Eigen::Matrix3d Rc;
  Rc << b1c, b2c, b3c;

  vel_b_(0) = msg.linear.x;
  vel_b_(1) = msg.linear.y;
  vel_b_(2) = msg.linear.z;

  if (!initialized)
  {
    // initialized = true;
    cmd_pos_(0) = msg.position.x;
    cmd_pos_(1) = msg.position.y;
    // if(mode == 1){
    //   cmd_pos_(2) = HEIGHT_OFFSET;
    // }
    // else if(mode == 2){
      cmd_pos_(2) = msg.position.z;
    // }
    cmd_yaw_ = atan2(b1c(1), b1c(0));
  }

  // if(abs(msg.linear.x) > 3 || abs(cmd_vel_b_(0)) > 0.5){
  //   cmd_vel_b_(0) = cmd_vel_b_(0) * msg.linear.x / cmd_vel_b_(0);
  // }
  // if(abs(msg.linear.y) > 3 || abs(cmd_vel_b_(1)) > 0.5){
  //   cmd_vel_b_(1) = cmd_vel_b_(1) * msg.linear.y / cmd_vel_b_(1);
  // }
  Eigen::Vector3d cmd_vel = Rc * cmd_vel_b_;
  Eigen::Vector3d vel = Rc * vel_b_;
  // Eigen::Vector3d cmd_vel = cmd_vel_b_;
  double vel_2D = sqrt(vel(0) * vel(0) + vel(1) * vel(1));
  double vel_2D_tar = sqrt(cmd_vel(0) * cmd_vel(0) + cmd_vel(1) * cmd_vel(1));
  // if(vel_2D > 3 || vel_2D_tar > 0.5){
  //   cmd_pos_(0) = cmd_pos_(0) + vel(0) * state_period;
  //   cmd_pos_(1) = cmd_pos_(1) + cmd_vel(1) * state_period;
  //   cmd_pos_(2) = cmd_pos_(2) + cmd_vel(2) * state_period;
  // }
  // else{
    cmd_pos_ = cmd_pos_ + cmd_vel * state_period;
  // }
  // if(abs(msg.linear.x) > 3 || abs(cmd_vel(0)) > 0.5){
  //   cmd_pos_(0) = msg.position.x;
  // }
  // if(abs(msg.linear.y) > 3 || abs(cmd_vel(1)) > 0.5){
  //   cmd_pos_(1) = msg.position.y;
  // }
  // if(vel_2D > 3 || vel_2D_tar > 0.5){
  //   cmd_pos_(0) = msg.position.x;
  //   // cmd_pos_(1) = msg.position.y;
  //   // printf("follow\n");
  //   // if(vel_2D_tar < 0.5){
  //   //   cmd_pos_(0) = cmd_pos_(0) + vel_b_(0) * state_period;
  //   //   cmd_pos_(1) = cmd_pos_(1) + vel_b_(1) * state_period;
  //   // }
  // }
  // printf("px = %f, py = %f\n",cmd_pos_(0), cmd_pos_(1));
  cmd_yaw_ = cmd_yaw_ + cmd_yawrate_ * state_period;
  static Eigen::Vector3d prev_cmd_vel = cmd_vel;
  Eigen::Vector3d cmd_acc = (cmd_vel - prev_cmd_vel) / state_period;
  prev_cmd_vel = cmd_vel;

  joy2pos.axes[0] = cmd_pos_(0);
  joy2pos.axes[1] = cmd_pos_(1);
  joy2pos.axes[2] = cmd_pos_(2);
  joy2pos.axes[3] = cmd_vel(0);
  joy2pos.axes[4] = cmd_vel(1);
  joy2pos.axes[5] = cmd_vel(2);
  joy2pos.axes[6] = cmd_acc(0);
  joy2pos.axes[7] = cmd_acc(1);
  joy2pos.axes[8] = cmd_acc(2);
  joy2pos.axes[9] = cmd_yaw_;

}
