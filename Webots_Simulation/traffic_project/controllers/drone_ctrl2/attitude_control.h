#include <Eigen/Eigen>
#include "user_public.h"


#define J11 0.0341171
#define J22 0.0363089
#define J33 0.0627386
#define J12 0
#define J13 0
#define J23 0
#define KR1 4
#define KR2 4
#define KR3 2
#define KOM1 0.7
#define KOM2 0.7
#define KOM3 0.7
#define KF           2.55e-5 //  N  per rad/s
#define KM           5.1e-7  //  Nm per rad/s
#define ARM_LENGTH   0.22978 //  m
#define POSITIVE(x) (x < 0 ? 0 : x)

class AttitudeControl
{
public:
  AttitudeControl();
  ~AttitudeControl();
  usrPublic::Joy att2ctrl = {}; // The height control node sends to the actual motor control volume
  void cmdCb(usrPublic::Pose msg);
  void stateCb(usrPublic::Odometry msg);
private:
  Eigen::Matrix3d Rd_;
  Eigen::Vector3d fd_;
};

AttitudeControl::AttitudeControl()
{
  // init matrix
  Rd_ = Eigen::Matrix3d::Identity();
  fd_ = Eigen::Vector3d::Zero();
}

AttitudeControl::~AttitudeControl() {}

void AttitudeControl::cmdCb(usrPublic::Pose msg)
{
  Eigen::Quaterniond qd(msg.orientation.w,
                        msg.orientation.x,
                        msg.orientation.y,
                        msg.orientation.z);
  Rd_ = qd.matrix();
  fd_(0) = msg.position.x;
  fd_(1) = msg.position.y;
  fd_(2) = msg.position.z;
}

void AttitudeControl::stateCb(usrPublic::Odometry msg)
{
  Eigen::Quaterniond q(msg.orientation.w,
                       msg.orientation.x, 
                       msg.orientation.y,
                       msg.orientation.z);
  Eigen::Matrix3d R  = q.matrix();

  double R11 = R(0, 0);
  double R12 = R(0, 1);
  double R13 = R(0, 2);
  double R21 = R(1, 0);
  double R22 = R(1, 1);
  double R23 = R(1, 2);
  double R31 = R(2, 0);
  double R32 = R(2, 1);
  double R33 = R(2, 2);

  double Rd11 = Rd_(0, 0);
  double Rd12 = Rd_(0, 1);
  double Rd13 = Rd_(0, 2);
  double Rd21 = Rd_(1, 0);
  double Rd22 = Rd_(1, 1);
  double Rd23 = Rd_(1, 2);
  double Rd31 = Rd_(2, 0);
  double Rd32 = Rd_(2, 1);
  double Rd33 = Rd_(2, 2);

  double psi = 0.5 * (3.0 - (Rd11 * R11 + Rd21 * R21 + Rd31 * R31 + 
                             Rd12 * R12 + Rd22 * R22 + Rd32 * R32 +
                             Rd13 * R13 + Rd23 * R23 + Rd33 * R33));
  if (psi > 1)
  {
    // printf("psi > 1, value = %lf\n", psi);
  }

  double eR1 = 0.5 * (R12 * Rd13 - R13 * Rd12 + R22 * Rd23 - R23 * Rd22 + R32 * Rd33 - R33 * Rd32);
  double eR2 = 0.5 * (R13 * Rd11 - R11 * Rd13 + R23 * Rd21 - R21 * Rd23 + R33 * Rd31 - R31 * Rd33);
  double eR3 = 0.5 * (R11 * Rd12 - R12 * Rd11 + R21 * Rd22 - R22 * Rd21 + R31 * Rd32 - R32 * Rd31);

  double Om1 = msg.angular.x;
  double Om2 = msg.angular.y;
  double Om3 = msg.angular.z;

  double eOm1 = Om1;
  double eOm2 = Om2;
  double eOm3 = Om3;

  Eigen::Matrix3d J = Eigen::Matrix3d::Identity();
  J(0, 0) = J11;
  J(0, 1) = J12;
  J(0, 2) = J13;
  J(1, 0) = J12;
  J(1, 1) = J22;
  J(1, 2) = J23;
  J(2, 0) = J13;
  J(2, 1) = J23;
  J(2, 2) = J33;
  Eigen::Vector3d Om;
  Om(0) = Om1;
  Om(1) = Om2;
  Om(2) = Om3;
  Eigen::Vector3d comp = Om.cross(J * Om);

  double f = POSITIVE(R13 * fd_(0) + R23 * fd_(1) + R33 * fd_(2));
  double M1 = -KR1   * eR1 - KOM1 * eOm1 + comp(0);
  double M2 = -KR2   * eR2 - KOM2 * eOm2 + comp(1);
  double M3 = -KR3   * eR3 - KOM3 * eOm3 + comp(2);

  double thrust[4];
  thrust[0] = 0.25 * (f - M1 / ARM_LENGTH - M2 / ARM_LENGTH - M3 / (KM / KF));
  thrust[1] = 0.25 * (f + M1 / ARM_LENGTH - M2 / ARM_LENGTH + M3 / (KM / KF));
  thrust[2] = 0.25 * (f + M1 / ARM_LENGTH + M2 / ARM_LENGTH - M3 / (KM / KF));
  thrust[3] = 0.25 * (f - M1 / ARM_LENGTH + M2 / ARM_LENGTH + M3 / (KM / KF));

  for (int i = 0; i < 4; i++)
  {
    if (thrust[i] < 0)
    {
      thrust[0] -= thrust[i];
      thrust[1] -= thrust[i];
      thrust[2] -= thrust[i];
      thrust[3] -= thrust[i];
    }
  }

  double w1 =  sqrt(thrust[0] / KF);
  double w2 = -sqrt(thrust[1] / KF);
  double w3 =  sqrt(thrust[2] / KF);
  double w4 = -sqrt(thrust[3] / KF);
  
  att2ctrl.axes[0] = w1;
  att2ctrl.axes[1] = w2;
  att2ctrl.axes[2] = w3;
  att2ctrl.axes[3] = w4;
}
