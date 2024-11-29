#pragma once
#include <Eigen/Eigen>
#include "user_public.h"
#include "json_config_handle.h"
#include <string>


#define KX1 8
#define KX2 8
#define KX3 17
#define KV1 10
#define KV2 10
#define KV3 10
#define IV1 0.1
#define IV2 0.1
#define IV3 0.1
#define MASS 3.
#define G 9.8
#define MAX_TILT M_PI / 5 // body tilt limit
// #define MAX_TILT 0

class PositionControl
{
public:
  PositionControl();
  ~PositionControl();
  usrPublic::Pose pos2att = {};
  void stateCb(usrPublic::Odometry state,const configData_s *cfg);
  void cmdCb(usrPublic::Joy msg);
  bool done = false;
  std::string done_state = "none";
private:
  double des_yaw_;
  Eigen::Vector3d des_pos_;
  Eigen::Vector3d des_vel_;
  Eigen::Vector3d des_acc_;
  bool done_check(usrPublic::Odometry state, Eigen::Vector3d _pos_err,const configData_s *cfg);
};

PositionControl::PositionControl()
{
  des_yaw_ = 0;
  des_pos_ = Eigen::Vector3d::Zero();
  des_vel_ = Eigen::Vector3d::Zero();
  des_acc_ = Eigen::Vector3d::Zero();
}

PositionControl::~PositionControl() {}

void PositionControl::cmdCb(usrPublic::Joy msg)
{
  des_yaw_ = msg.axes[9];
  des_pos_.x() = msg.axes[0];
  des_pos_.y() = msg.axes[1];
  des_pos_.z() = msg.axes[2];
  des_vel_.x() = msg.axes[3];
  des_vel_.y() = msg.axes[4];
  des_vel_.z() = msg.axes[5];
  des_acc_.x() = msg.axes[6];
  des_acc_.y() = msg.axes[7];
  des_acc_.z() = msg.axes[8];
}

void PositionControl::stateCb(usrPublic::Odometry state,const configData_s *cfg)
{
  Eigen::Vector3d pos(state.position.x,
                      state.position.y,
                      state.position.z);
  Eigen::Vector3d vel(state.linear.x,
                      state.linear.y,
                      state.linear.z);
  Eigen::Vector3d pos_err = des_pos_ - pos;
  Eigen::Vector3d vel_err = des_vel_ - vel;
  Eigen::Vector3d kx(KX1, KX2, KX3);
  Eigen::Vector3d kv(KV1, KV2, KV3);
  Eigen::Vector3d force = kx.asDiagonal() * pos_err + kv.asDiagonal() * vel_err + MASS * des_acc_ + MASS * G * Eigen::Vector3d::UnitZ();

  // judge is done?
  done = done_check(state, pos_err, cfg);

  // limit tilt angle to MAX_TILT
  double c = cos(MAX_TILT);
  if (Eigen::Vector3d(0, 0, 1).dot(force.normalized()) < c) {
    Eigen::Vector3d f = force - MASS * G * Eigen::Vector3d::UnitZ();
    double nf = f.norm();
    double A = c * c * nf * nf - f(2) * f(2);
    double B = 2 * (c * c - 1) * f(2) * MASS * G;
    double C = (c * c - 1) * MASS * MASS * G * G;
    double s = (-B + sqrt(B * B - 4 * A * C)) / (2 * A);
    force = s * f + MASS * G * Eigen::Vector3d::UnitZ();
  }

  Eigen::Vector3d b1c, b2c, b3c;
  Eigen::Vector3d b1d(cos(des_yaw_), sin(des_yaw_), 0);
  if (force.norm() < 1e-7)
    b3c = Eigen::Vector3d::UnitZ();
  else
    b3c = force.normalized();
  b2c = b3c.cross(b1d).normalized();
  b1c = b2c.cross(b3c).normalized();
  Eigen::Matrix3d Rc;
  Rc << b1c, b2c, b3c;
  Eigen::Quaterniond qc(Rc);

  pos2att.position.x = force(0);
  pos2att.position.y = force(1);
  pos2att.position.z = force(2);
  pos2att.orientation.x = qc.x();
  pos2att.orientation.y = qc.y();
  pos2att.orientation.z = qc.z();
  pos2att.orientation.w = qc.w();
}

bool PositionControl::done_check(usrPublic::Odometry state, Eigen::Vector3d _pos_err,const configData_s *cfg){
    bool _done = false;
    Eigen::Vector2d pos_err(_pos_err(0),_pos_err(1));
    double dist_err = pos_err.norm();
    Eigen::Vector2d Vxy(state.linear.x,state.linear.y);
    double v = Vxy.norm();
    // height
    if((state.position.z < cfg->droneRange.minHeight) || (state.position.z > cfg->droneRange.maxHeight)){
      _done = true;
      done_state = "height";
    }// distance error
    else if(dist_err > cfg->droneRange.distanceError){
      _done = true;
      done_state = "distance";
    }// speed error
    else if(v >= cfg->droneRange.velocity){
      _done = true;
      done_state = "velocity";
    }// yaw velocity
    else if(abs(state.angular.z) > cfg->droneRange.omiga){
      _done = true;
      done_state = "yaw velocity";
    }// pitch and roll
    else if((abs(state.angle.x) > cfg->droneRange.roll) || (abs(state.angle.y) > cfg->droneRange.pitch)){
      _done = true;
      done_state = "pitch or yaw angle";
    }
    return _done;
}