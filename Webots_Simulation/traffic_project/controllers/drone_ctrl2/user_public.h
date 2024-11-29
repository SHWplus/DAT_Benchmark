#pragma once
#include <iostream>
#include <stdint.h>


namespace usrPublic{
    #pragma pack(1)
    typedef struct _vector3{
        double x;
        double y;
        double z;
    }vector3;
    #pragma pack()

    #pragma pack(1)
    typedef struct _vector4{
        double w;
        double x;
        double y;
        double z;
    }vector4;
    #pragma pack()

    // sensor data and reward and done ---- double * 22
    #pragma pack(1)
    typedef struct _Odometry{
        double t;
        vector3 position;   //m
        vector3 linear;     //m/s
        vector3 acc;        //m/s^2
        vector3 angular;    //rad
        vector4 orientation;
        vector3 angle;      //euler
        double reward;      //reward
        double done;        //is done
    }Odometry;
    #pragma pack()

    // make reward data ---- double * 60 + string
    #pragma pack(1)
    typedef struct _rewardData{
        double cameraWidth;     // pixels
        double cameraHeight;    // pixels
        double cameraFov;       // rad
        double cameraF;         // pixels
        double cameraPitch;     // rad
        double trackerHeight;   // m 
        double initDirection;   // rad
        double T_ct[16];        // Transformation matrix of the camera with respect to the world coordinate system
        // vector3 BMW;         // car sizes
        // vector3 Citroen;
        // vector3 Lincoln;
        // vector3 Benz;
        // vector3 Rover;
        // vector3 Tesla;
        // vector3 Toyota;
        double T_tw[16];// Transformation matrix of the vehicle with respect to the world coordinate system
        vector3 cameraMidGlobalPos;// The center of the camera is mapped to the 3D coordinates of the ground in the world coordinate system.
        vector3 carMidGlobalPos;// 3D coordinates of the vehicle center in the world coordinate system
        vector3 cameraMidPos; // Coordinates of the camera center in the world coordinate system
        vector4 carDronePosOri; // 3D coordinates and 1D attitude of vehicle center in UAV coordinate system
        vector3 carDroneVel; // 3D velocity of the vehicle center in the UAV coordinate system
        vector3 carDroneAcc; // 3D acceleration of vehicle center in UAV coordinate system
        double crash; // Whether the drone collided with a building
        double carDir;// Vehicle running direction (0 stop, 1 forward, 2 left turn, 3 right turn)
        std::string carTypename = std::string("BmwX5Simple");// object type
    }rewardData;
    #pragma pack()

    #pragma pack(1)
    typedef struct _Pose{
        vector4 orientation;
        vector3 position;
    }Pose;
    #pragma pack()

    #pragma pack(1)
    typedef struct _Joy{
        double axes[10];
    }Joy;
    #pragma pack()
}
