#include <cmath>
#include <Eigen/Eigen>
#include <iostream>
#include <math.h>
#include "../drone_ctrl2/user_public.h"
using namespace Eigen;

class camera2real
{
private:
    double hyperbolic_tangent_func(double input, double scale);

public:
    camera2real() {};
    ~camera2real() {};

    Vector3d Location_of_Camera_Calculate(Vector2d target_on_camera_uv,
                                          // const double f,const double camera_pitch, const double camera_yaw,
                                          const Matrix<double, 3, 4> T_land_of_camera,
                                          const double fov_horizon = 0.785398,
                                          const Vector2d image_size_hw = Vector2d(240, 320));
    Vector3d Location_of_World_Calculate(const Vector3d location_of_camera, const Matrix<double, 3, 4> T_camera_of_land, const Matrix<double, 3, 4> T_land_of_world);
    double Get_Location_Reward(const Vector3d tracking_location, const Vector3d follow_location, const Vector3d target_real_world_location, const double range, const double scale);
    double Get_Location_Reward(const Vector3d follow_location, const Vector3d target_real_world_location, const double range);
    double Get_Location_Reward(const Vector3d follow_location, const Vector3d target_real_world_location, const double range, const double scale);
    double cameraF;
    double Get_View_Proportions(Vector3d* follow_location, const Vector3d& target_real_world_location);
    double Get_View_Reward(Vector3d* follow_location, const Vector3d& target_real_world_location);
    double Get_View_Reward(Vector3d* follow_location, const Vector3d& target_real_world_location, const double scale);
};

/**
 * @brief Pixel coordinates to camera coordinates
 *
 * @param target_on_camera_uv: Pixel coordinates of the target
 * @param T_land_of_camera: Chi-Transform Matrix from Ground to Camera
 * @param fov_horizon: Horizontal field of view of the camera
 * @param image_size_hw: Image size height * width
 * @return Vector3d Coordinates of the target relative to the lens
 */
inline Vector3d camera2real::Location_of_Camera_Calculate(Vector2d target_on_camera_uv, const Matrix<double, 3, 4> T_land_of_camera, const double fov_horizon, const Vector2d image_size_hw)
{
    // Plane equation of the ground (bridge) with respect to the camera coordinates (normal vector ABC with passing point xyz,6D)
    Vector<double, 6> land_equation(T_land_of_camera(0, 2), T_land_of_camera(1, 2), T_land_of_camera(2, 2),
                                    T_land_of_camera(0, 3), T_land_of_camera(1, 3), T_land_of_camera(2, 3));
    // Camera Pixel Focal Length Estimation
    cameraF = (image_size_hw[1] / 2.0) / tan(fov_horizon / 2);
    // Calculation of equation coefficients
    double D = -T_land_of_camera(0, 2) * T_land_of_camera(0, 3) - T_land_of_camera(1, 2) * T_land_of_camera(1, 3) - T_land_of_camera(2, 2) * T_land_of_camera(2, 3);

    double x0 = cameraF;
    double y0 = image_size_hw[1] / 2 - target_on_camera_uv[0];
    double z0 = image_size_hw[0] / 2 - target_on_camera_uv[1];
    // Solving for the coordinates of the target relative to the camera coordinate system
    Vector3d target_Camera_location_xyz;
    // Solve the equation to obtain the XYZ of the target in the lens coordinate system.
    target_Camera_location_xyz[0] = (-x0 * D) / (land_equation[0] * x0 + land_equation[1] * y0 + land_equation[2] * z0);
    target_Camera_location_xyz[1] = (-y0 * D) / (land_equation[0] * x0 + land_equation[1] * y0 + land_equation[2] * z0);
    target_Camera_location_xyz[2] = (-z0 * D) / (land_equation[0] * x0 + land_equation[1] * y0 + land_equation[2] * z0);

    // Vertical field of view of the camera
    Vector3d top_FOV_vec(1, 0, tan(0.5 * fov_horizon));
    Vector3d bottom_FOV_vec(1, 0, -tan(0.5 * fov_horizon));
    Vector3d land_n_vec(land_equation[0], land_equation[1], land_equation[2]);
    double fov_verticle = 2 * atan(tan(fov_horizon * 0.5) * (image_size_hw[0] / image_size_hw[1]));

    // Pitch angle too high alarm
    if ((top_FOV_vec.dot(land_n_vec)) >= 0 || bottom_FOV_vec.dot(land_n_vec) >= 0)
    {
        // std::cerr << "camera pitch too high" << std::endl;
    }

    return target_Camera_location_xyz;
}

/**
 * @brief Convert the target point in the camera coordinate system to the world coordinate system.
 *
 * @param location_0f_camera
 * @param T_camera_of_land
 * @param T_land_of_world
 * @return Vector3d
 */
inline Vector3d camera2real::Location_of_World_Calculate(const Vector3d location_of_camera, const Matrix<double, 3, 4> T_camera_of_land, const Matrix<double, 3, 4> T_land_of_world)
{
    Matrix<double, 4, 4> T_camera_of_land_;
    T_camera_of_land_ << T_camera_of_land, 0, 0, 0, 1;
    Matrix<double, 4, 4> T_land_of_world_;
    T_land_of_world_ << T_land_of_world, 0, 0, 0, 1;
    Vector4d location_of_camera_;
    location_of_camera_ << location_of_camera, 1;

    Vector4d location_of_world_ = T_land_of_world_ * T_camera_of_land_ * location_of_camera_;
    Vector3d location_of_world(location_of_world_[0], location_of_world_[1], location_of_world_[2]);
    return location_of_world;
}

/**
 * @brief hyperbolic tangent function
 *
 * @param input
 * @param scale Custom Domain Scaling
 * @return double
 */
inline double camera2real::hyperbolic_tangent_func(double input, double scale)
{
    double real_input = pow(input, 3) * scale;
    // double k1 = std::exp(real_input);
    // double k2 = std::exp(-real_input);
    // double out = double((k1 - k2) / (k1 + k2));
    double k = std::exp(-2. * real_input);
    double out = double((1 - k) / (1 + k));
    // std::cout<<"real_input: "<<real_input<<"  out: "<< out<<std::endl;
    return out;
}

/**
 * @brief Based on camera target point, tracking position, true position of vehicle is rewarded (baseLine version)
 *
 * @param tracking_location: Coordinates of the projection point obtained by tracking
 * @param follow_location: Coordinates of the projection point of the desired tracking point
 * @param target_real_world_location: Tracking the true coordinates of the target
 * @param range: Acceptable target range
 * @param scale: Distance decrease scale
 * @return double
 */
inline double camera2real::Get_Location_Reward(const Vector3d tracking_location, const Vector3d follow_location, const Vector3d target_real_world_location, const double range, const double scale)
{
    Vector2d follow, target, tracking;
    follow << follow_location(0), follow_location(1);
    target << target_real_world_location(0), target_real_world_location(1);
    tracking << tracking_location(0), tracking_location(1);
    double tracking_dis = (tracking - target).norm();
    // double follow_dis = (follow_location - target_real_world_location).norm();
    double follow_dis = (follow - tracking).norm();
    double reward = double(tracking_dis < range) - hyperbolic_tangent_func(follow_dis, scale);
    if (reward < 0 || std::isnan(reward) || std::isinf(reward))
    {
        reward = 0;
    }
    return reward;
}
/**
 * @description: ALG version1
 * @param {Vector3d} follow_location
 * @param {Vector3d} target_real_world_location
 * @param range Acceptable target range
 * @return {*}
 */
inline double camera2real::Get_Location_Reward(const Vector3d follow_location, const Vector3d target_real_world_location, const double range)
{
    Vector2d follow, target;
    follow << follow_location(0), follow_location(1);
    target << target_real_world_location(0), target_real_world_location(1);
    double tracking_dis = (follow - target).norm();
    return double(tracking_dis < range);
}

/**
 * @description: ALG version2
 * @param {Vector3d} follow_location
 * @param {Vector3d} target_real_world_location
 * @param range Acceptable target range
 * @param scale Distance decrease scale
 * @return {*}
 */
inline double camera2real::Get_Location_Reward(const Vector3d follow_location, const Vector3d target_real_world_location, const double range, const double scale)
{
    Vector2d follow, target;
    follow << follow_location(0), follow_location(1);
    target << target_real_world_location(0), target_real_world_location(1);
    double tracking_dis = (follow - target).norm();
    double reward = double(tracking_dis < range) - hyperbolic_tangent_func(tracking_dis, scale);
    if (reward < 0 || std::isnan(reward) || std::isinf(reward))
    {
        reward = 0;
    }
    return reward;
}

inline double camera2real::Get_View_Proportions(Vector3d* follow_location, const Vector3d& target_real_world_location)
{
    int sector = 0;
    double line_angle[4];
    // Calculate the angles of the four dividing lines
    for (int i = 0; i < 4; i++)
    {
        line_angle[i] = atan2(follow_location[i + 1](1) - follow_location[0](1), follow_location[i + 1](0) - follow_location[0](0));
    }
    // Calculate the angle of the target
    double follow_angle = atan2(target_real_world_location(1) - follow_location[0](1), target_real_world_location(0) - follow_location[0](0));
    double line_angle_max = 0, line_angle_min = 0;
    int max_idx = 0, min_idx = 0;
    for (int i = 0; i < 4; i++)
    {
        if (line_angle[i] > line_angle_max)
        {
            line_angle_max = line_angle[i];
            max_idx = i;
        }
        if (line_angle[i] < line_angle_min)
        {
            line_angle_min = line_angle[i];
            min_idx = i;
        }
        if (i == 3)
        {
            if ((follow_angle > line_angle[i] && follow_angle < line_angle[0]))
            {
                sector = i + 1;
            }
        }
        else
        {
            if ((follow_angle > line_angle[i] && follow_angle < line_angle[i + 1]))
            {
                sector = i + 1;
                // std::cout << i << std::endl;
            }
        }
        if (sector != 0)
        {
            break;
        }
    }
    if (sector == 0)
    {
        if(abs(max_idx - min_idx) == 1)
        {
            sector = (max_idx>min_idx)?min_idx:max_idx + 1;
        }
        else
        {
            sector = 4;
        }
    }
    
    // Calculate the two lines for which the ratio is to be determined
    Vector2d follow_line;
    Vector2d edge_line;
    follow_line(0) = (target_real_world_location(1) - follow_location[0](1)) / (target_real_world_location(0) - follow_location[0](0));
    follow_line(1) = follow_location[0](1) - follow_line(0) * follow_location[0](0);
    if (sector == 4)
    {
        edge_line(0) = (follow_location[1](1) - follow_location[4](1)) / (follow_location[1](0) - follow_location[4](0));
    }
    else
    {
        edge_line(0) = (follow_location[sector + 1](1) - follow_location[sector](1)) / (follow_location[sector + 1](0) - follow_location[sector](0));
    }
    edge_line(1) = follow_location[sector](1) - edge_line(0) * follow_location[sector](0);
    // Calculate the point of intersection of the two lines
    Vector2d cross_point;
    cross_point(0) = (follow_line(1) - edge_line(1)) / (edge_line(0) - follow_line(0));
    cross_point(1) = edge_line(0) * (follow_line(1) - edge_line(1)) / (edge_line(0) - follow_line(0)) + edge_line(1);
    // Calculated Distance
    Vector2d follow, target;
    follow << follow_location[0](0), follow_location[0](1);
    target << target_real_world_location(0), target_real_world_location(1);
    double follow_dist = (follow - target).norm();
    double edge_dist = (follow - cross_point).norm();
    double proportions = follow_dist / edge_dist;
    if (proportions > 1)
    {
        proportions = 1;
    }
    return (1. - proportions);
}

inline double camera2real::Get_View_Reward(Vector3d* follow_location, const Vector3d& target_real_world_location)
{
    double p = Get_View_Proportions(follow_location,target_real_world_location);
    return (p>0)?1:0;
}

inline double camera2real::Get_View_Reward(Vector3d* follow_location, const Vector3d& target_real_world_location, const double scale)
{
    double p = Get_View_Proportions(follow_location,target_real_world_location);
    return hyperbolic_tangent_func(p, scale);
}