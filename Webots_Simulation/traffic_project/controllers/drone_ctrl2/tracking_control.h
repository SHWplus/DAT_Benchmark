#pragma once
#include <../../libraries/myLibs/Upper_Public.h>
#include <Eigen/Eigen>
#include "user_public.h"
#include <../../libraries/myLibs/PIDmethod.h>
#include <../../libraries/myLibs/SecondButterworthLPF.h>
#include <Eigen/Dense>

#define BODY2GIMBAL_D 0.13   //Distance from the center of the body to the center of the 3-axis gimbal base
#define GIMBAL2CAMERA_D 0.04 //Distance from the center of the head base to the center of the camera

class TrackingCtrl
{
public:
    TrackingCtrl(double _timeStep);
    ~TrackingCtrl();
    void stateCb(usrPublic::Odometry state, usrPublic::vector3 gimbal_state);// drone state and gimbal state
    void cmdCb(usrPublic::vector4 msg);// The four-dimensional inputs in the image need to be passed in to compute the corresponding outputs
    usrPublic::vector4 track2joy = {};
private:
    PIDmethod drone_pid[4];// drone pid
    Eigen::Transform<double, 3, Eigen::Affine> transform;
    Eigen::Matrix3d rotation;
    usrPublic::Odometry state;
    double state_period; 
    double linear_speed[3] = {0};
    SecondOrderButterworthLPF tracking_f[4];

};

/**
 * @description: construction func
 * @param {double} _timeStep
 * @return {*}
 */
TrackingCtrl::TrackingCtrl(double _timeStep): state_period(_timeStep) {

    // translation vector
    Eigen::Translation3d translation(BODY2GIMBAL_D, 0, -GIMBAL2CAMERA_D);
    // rotation matrix
    rotation = Eigen::Matrix3d::Identity();
    // transformation matrix
    transform = translation * rotation;
    // init pid
    for(int i = 0; i < 4 ; i++){
        drone_pid[i].PID_Init(Common, state_period);
        tracking_f[i].init(25,1000 / state_period);
    }
    // drone_pid[0].Params_Config(25, 0.001, 200, 0., 25, -25);//x move
    // drone_pid[0].d_of_current = false;
    // drone_pid[1].Params_Config(-15, -0.01, -400, 0., 15, -15);//y move
    // drone_pid[1].d_of_current = false;
    drone_pid[0].Params_Config(12, 0.01, -0.025, 2., 12, -12);//x move
    drone_pid[1].Params_Config(-12, -0.01, -0.025, 2., 12, -12);//y move
    drone_pid[2].Params_Config(0.02, 0, -0.001, 0, 0.01, -0.01);//z move
    drone_pid[3].Params_Config(-60.,0.,-4,0,100,-100);//z turn
    

}

TrackingCtrl::~TrackingCtrl() {}

/**
 * @description: update tracking state
 * @param {Odometry} _state
 * @param {vector3} gimbal_state
 * @return {*}
 */
void TrackingCtrl::stateCb(usrPublic::Odometry _state, usrPublic::vector3 gimbal_state){
    usrPublic::Odometry state = _state;
    linear_speed[0] = state.linear.x;
    linear_speed[1] = state.linear.y;
    linear_speed[2] = state.linear.z;
    // update transformation matrix
    Eigen::Translation3d translation(BODY2GIMBAL_D * cos(state.angle.y) - GIMBAL2CAMERA_D * sin(state.angle.y), 0, -GIMBAL2CAMERA_D * cos(state.angle.y) - BODY2GIMBAL_D * sin(state.angle.y));
    // Eigen::AngleAxisd rotation_bz(state.angle.z, Eigen::Vector3d::UnitZ());
    Eigen::AngleAxisd rotation_by(state.angle.y, Eigen::Vector3d::UnitY());
    Eigen::AngleAxisd rotation_bx(state.angle.x, Eigen::Vector3d::UnitX());
    Eigen::AngleAxisd rotation_z(gimbal_state.z, Eigen::Vector3d::UnitZ());
    Eigen::AngleAxisd rotation_y(gimbal_state.y, Eigen::Vector3d::UnitY());
    Eigen::AngleAxisd rotation_x(gimbal_state.x, Eigen::Vector3d::UnitX());
    rotation = (rotation_by * rotation_bx * rotation_z * rotation_y * rotation_x).toRotationMatrix();
    // rotation = (rotation_z * rotation_y * rotation_x).toRotationMatrix();
    transform = translation * rotation;

}

/**
 * @description: execute tracking control
 * @param {vector4} msg
 * @return {*}
 */
void TrackingCtrl::cmdCb(usrPublic::vector4 msg){
    Eigen::Vector3d v1_vector(tracking_f[0].f(0), tracking_f[1].f(msg.y), tracking_f[2].f(msg.z + 0.25 * cos(msg.w))); // Linear velocity vector in the working coordinate system
    // Eigen::Vector3d v1_vector(tracking_f[0].f(0), tracking_f[1].f(msg.y), tracking_f[2].f(msg.z)); // Linear velocity vector in the working coordinate system
    // std::cout<<"v1: \n"<<v1_vector.matrix()<<std::endl;
    Eigen::Vector3d v0_vector = rotation * v1_vector; // Linear velocity vector in the working coordinate system
    v0_vector(2) = 0;
    // std::cout<<"v2: \n"<<v0_vector.matrix()<<std::endl;

    for(int i = 0; i < 3 ; i++){
        drone_pid[i].target = v0_vector(i);
        drone_pid[i].current = 0;
        // if(i == 0 || i == 1){
        //     drone_pid[i].Adjust(0);
        //     // std::cout<<"error:  "<<drone_pid[0].error<<" "<< "i_term:  "<< drone_pid[0].I_Term<<"  "<<"d_tern: "<<drone_pid[0].D_Term<<std::endl;
        // }
        // else{
            drone_pid[i].Adjust(0, linear_speed[i]);
        // }
    }

    track2joy.x = drone_pid[0].out;
    track2joy.y = drone_pid[1].out;
    track2joy.z = drone_pid[2].out;
    track2joy.w = drone_pid[3].out;
}

