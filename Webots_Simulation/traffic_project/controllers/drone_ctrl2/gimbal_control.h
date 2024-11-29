#pragma once
#include <../../libraries/myLibs/PIDmethod.h>
#include <Eigen/Eigen>
#include "user_public.h"
#include <../../libraries/myLibs/SecondButterworthLPF.h>

#define Kpitch 4
#define Ipitch 0.02
#define Dpitch -0.001
#define Ipitchmax 0.1
#define Kyaw 4
#define Iyaw 0.02
#define Dyaw -0.001
#define Iyawmax 0.1
#define Kroll 2
#define Iroll 0.02
#define Droll -0.0005
#define Irollmax 0.1

class GimbalControl{
public:
    GimbalControl(double _timeStep);
    ~GimbalControl();
    void stateCb(usrPublic::Odometry state, usrPublic::vector3 gimbal_state);// update basic states
    void cmdCb(usrPublic::vector3 msg);// control calculation and output
    void updateConstrain(double* p);
    usrPublic::Joy gbl2ctrl = {};
    double theta[3] = {0};
private:
    PIDmethod gimbalPid[3];//order x-y-z
    SecondOrderButterworthLPF tarF[3];
    Eigen::Matrix3d rotation;       // This rotation matrix is expressed as the rotation matrix of the lens at the end of the gimbal
    Eigen::AngleAxisd rotation_comp;// The rotation caused by the tilting of the body is compensated by the matrix.
    void GimbalIk();                // The parameters have been updated by default here
    Eigen::MatrixXd angle_constrain = Eigen::MatrixXd::Identity(3, 2);
};

/**
 * @description: construction func
 * @param {double} _timeStep
 * @return {*}
 */
GimbalControl::GimbalControl(double _timeStep){
    for(int i = 0; i<3; i++){
        gimbalPid[i].PID_Init(Common,_timeStep);
        tarF[i].init(20, 1./_timeStep);
    }
    gimbalPid[0].Params_Config(Kroll,Iroll,Droll,Irollmax,1,-1);
    gimbalPid[1].Params_Config(Kpitch,Ipitch,Dpitch,Ipitchmax,1,-1);
    gimbalPid[2].Params_Config(Kyaw,Iyaw,Dyaw,Iyawmax,1,-1);
    
    // set rotation matrix
    rotation = Eigen::Matrix3d::Identity();

    // set 3 axises constrains
    angle_constrain(0, 0) = -1.7;
    angle_constrain(0, 1) = 1.7;
    angle_constrain(1, 0) = -0.5;
    angle_constrain(1, 1) = 1.5;
    angle_constrain(2, 0) = -1.7;
    angle_constrain(2, 1) = 1.7;

}

/**
 * @description: update gimbal pose constrains
 * @param: {double*} p
 * @return: {*}
 */
void GimbalControl::updateConstrain(double* p){
    angle_constrain(0, 0) = p[0];
    angle_constrain(0, 1) = p[1];
    angle_constrain(1, 0) = p[2];
    angle_constrain(1, 1) = p[3];
    angle_constrain(2, 0) = p[4];
    angle_constrain(2, 1) = p[5];
}

GimbalControl::~GimbalControl() {}

/**
 * @description: state update function
 * @param {Odometry} state
 * @param {vector3} gimbal_state
 * @return {*}
 */
void GimbalControl::stateCb(usrPublic::Odometry state, usrPublic::vector3 gimbal_state){
    gimbalPid[0].current = gimbal_state.x;
    gimbalPid[1].current = gimbal_state.y;
    gimbalPid[2].current = gimbal_state.z;

    // Get the state of the body and compute the inverse rotation matrix.
    Eigen::AngleAxisd rotation_Ix(-state.angle.x, Eigen::Vector3d::UnitX());
    Eigen::AngleAxisd rotation_Iy(-state.angle.y, Eigen::Vector3d::UnitY());
    rotation_comp = rotation_Ix * rotation_Iy;
}

/**
 * @description: Control function
 * @param {vector3} msg
 * @return {*}
 */
void GimbalControl::cmdCb(usrPublic::vector3 msg){
    // The small triaxial inverse solution is solved based on the target rotation combined with the compensation matrix, and the Pid control
    Eigen::AngleAxisd rotation_z(msg.z, Eigen::Vector3d::UnitZ());
    Eigen::AngleAxisd rotation_y(msg.y, Eigen::Vector3d::UnitY());
    Eigen::AngleAxisd rotation_x(msg.x, Eigen::Vector3d::UnitX());
    rotation = (rotation_comp * rotation_z * rotation_y * rotation_x).toRotationMatrix();

    GimbalIk();

    for(int i = 0; i<3; i++){
        gimbalPid[i].target = tarF[i].f(upper::constrain(theta[i],angle_constrain(i,0),angle_constrain(i,1)));
        // std::cout<<i<<"  "<<gimbalPid[i].target<<std::endl;
        gbl2ctrl.axes[i] = gimbalPid[i].Adjust(0);
        gbl2ctrl.axes[i+3] = gimbalPid[i].target;
    }
}

/**
 * @description: ik in order z-y-x
 * @return {*}
 */
void GimbalControl::GimbalIk(){
    double r31 = rotation(2,0);
    double r32 = rotation(2,1);
    double r33 = rotation(2,2);
    double r21 = rotation(1,0);
    double r11 = rotation(0,0);
    theta[1] = atan2(-r31,sqrt(pow(r32,2)+pow(r33,2)));
    upper::constrain(theta[1],angle_constrain(1,0),angle_constrain(1,1));
    theta[2] = atan2(r21/cos(theta[1]),r11/cos(theta[1]));
    upper::constrain(theta[2],angle_constrain(2,0),angle_constrain(2,1));
    theta[0] = atan2(r32/cos(theta[1]),r33/cos(theta[1]));
    upper::constrain(theta[0],angle_constrain(0,0),angle_constrain(0,1));
    // std::cout<<theta[0]<<"  "<<theta[1]<<"  "<<theta[2]<<std::endl;
}

