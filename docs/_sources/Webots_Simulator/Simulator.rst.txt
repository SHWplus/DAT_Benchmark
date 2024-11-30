Simulation Environment
=======================

    .. raw:: html

        <style>
            #language-switch {
            display: flex; /* Use Flexbox layout */
            justify-content: center; /* Center buttons horizontally */
            align-items: center; /* Center buttons vertically */
            gap: 10px; /* Space between buttons */
            margin-top: 20px;
            margin-bottom: 20px;
        }
        #language-switch button {
            width: 180px;
            height: 40px;
            font-size: 16px;
            padding: 10px;
            margin: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            background-color: #f0f0f0;
            display: flex;
            align-items: center; /* Center text vertically */
            justify-content: center; /* Center text horizontally */
        }
        </style>

        <!-- Language switch buttons -->
        <div id="language-switch" style="background-color: #fae3e3; padding: 15px; border-radius: 5px; border: 2px solid #cb7474;">
            <b style="font-size: 18px;">You can choose language by </b>
            <button onclick="switchLanguage('zh')">中文</button>
            <button onclick="switchLanguage('en')">English</button>
        </div>

        <script>
            function switchLanguage(lang) {
                if (lang === 'zh') {
                    window.location.href = '../../zh/Webots_Simulator/Simulator.html';
                } else if (lang === 'en') {
                    window.location.href = '../../en/Webots_Simulator/Simulator.html';
                }
            }
        </script>
        </br>
        <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
        </br>
        </br>

.. _Environment Introduction:

Environment Introduction
----------------------------------------

- The simulation environment of this project is built based on the open-source simulation software `webots <https://cyberbotics.com/>`_. The background of the simulation environment simulates the target tracking problem in outdoor scenes in real life. For this purpose, six maps have been set up, including city streets, city center, lakeside, countryside, desert, and farmland, each of which evolves into various conditions such as day, night, foggy, and snowy, making a total of 24 environments. To facilitate model training from simple environments, several simple environment maps are also available for use.
- Schematic diagrams of 24 simulation environments in the project:

.. image:: ../_static/image/24Scene_Colorful2.png
   :alt: 24个环境示意图
   :width: 700px
   :align: center

.. raw:: html

   </br>


.. _Operation Flow:

Operation Flow
------------------------------

.. raw:: html

   <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
      To accommodate different needs such as training, debugging, etc., this project offers <b>3 different running modes</b>.
   </div>
   </br>

.. image:: ../_static/image/ExampleImage.png
   :alt: Example Image
   :width: 700px
   :align: center

demo mode
~~~~~~~~~~~~~~~~~~

   This mode generates a tracker in the map. The tracker can fly through the map by keyboard operation, allowing you to browse the map. Meanwhile, the tracker by default tracks a BmwX5 vehicle near its initial position and outputs the reward parameters in real time on the Console status bar. This object can be used to test whether the built-in reward parameters are reasonable for debugging purposes.

      * :code:`up`: Drone forward

      * :code:`down`: Move the drone backward.

      * :code:`left`: Drone rotates vertically counterclockwise.

      * :code:`right`: Drone rotates vertically clockwise.

      * :code:`w` :code:`s` :code:`a` :code:`d`: Controls the rotation of the camera head up, down, left, right, and center.

      * :code:`shift` + :code:`up`: Raise the drone.

      * :code:`shift` + :code:`down`: Drop the drone.

      * :code:`shift` + :code:`left`: Drone pans left.

      * :code:`shift` + :code:`right`: Drone pans right.

.. raw:: html

   <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
      Note: At this point, rewards include both continuous and discrete rewards, see <b>built-in Reward</b> for details.
   </div>
   </br>

video mode
~~~~~~~~~~~~~~~~~~~

   - This mode is mainly used to record the behavior of the tracked object. The environment will automatically schedule the tracker error tracking object and export video images according to the simulation time and configuration parameters, while generating labels corresponding to each image.
   - The data is stored in: :code:`./Webots_Simulation/traffic_project/droneVideos/DRONEX/episodeX`, with the image format as jpeg and the labels in the :code:`mark.json` file.
   - At the same time, you can generate multiple sets of video image file structure descriptions through the script by directly executing the :code:`./Webots_Simulation/traffic_project/fileStruct.py` script, which will generate the description file :code:`dir_info.json` in the same directory.

training mode
~~~~~~~~~~~~~~~~~~~

   This mode is used for algorithm training. You can choose to manually open the Webots simulation first and then run the training script, or you can choose to modify the algorithm configuration file to achieve one-click full startup of the algorithm.

.. _Parameter configuration of the simulation environment:

Parameter Configuration
---------------------------------

   .. raw:: html

      <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
         All settings for the simulation environment in this project can be efficiently configured using <b>1 JSON file</b>.
      </div>
      </br>

   .. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        The configuration file for the simulation environment is: <code>Webots_Simulation/traffic_project/config/env_config.json</code>.
    </div>

Basic Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: json

   {
      "Simulation_Mode": "demo",
      "Tracker_Def": "DRONE",
      "Drone_Supervisor_Ctrl": true,
      "Socket_Ip": "127.0.0.1",
      "Config_Agen_Num_Port": 38711,
      "Train_Total_Steps": 1500,
      "Init_No_Done_Steps": 100,
      "No_Reward_Done_Steps": 100,
      "Control_Frequence": 125,
      "Customized_Rewards": true,
      "Lidar_Enable": false,
      "Tracking_Object": "SUMO_VEHICLE",
      "Verbose": false
   }

**Parameter Description**

   * :code:`Simulation_Mode` : There are three simulation modes: "demo", "video", and "train". The demo and video modes are self-running modes of the simulation (default is demo).

      * The demo will generate a tracker in the map, which supports direct control via the keyboard. Meanwhile, it will track a stationary vehicle, Bmx, by default. This mode can be used to browse the map or debug the reward parameters.
      * The video mode is the video shooting mode. In this mode, the tracker will automatically track the target object, exporting video images and labels.
      * train is the training mode, where the simulation end interacts with the algorithm end to train the tracking algorithm of the tracker.
      * For the complete system operation flowchart, see: :ref:`Operation Flow`

   - :code:`Tracker_Def` : Select the tracker, the current options are drone ("DRONE") and car ("CAR"). Among them, the drone is a simulated drone tracker with physical property detection and constraints, while the car is considered an ideal tracker that ignores its own physical properties and can perform any action under any circumstances.
   - :code:`Drone_Supervisor_Ctrl` : Whether to use the supervisor to control the tracker. The supervisor is Webots' super administrator and can directly control any node. If true, the supervisor controls the tracker, and all its actions are real-time and responsive, which simplifies algorithm training. If false, the tracker is controlled using a traditional PID controller. This parameter is only applicable to the drone tracker; the car tracker always uses the supervisor for control.
   - :code:`Socket_Ip` : The IP address for socket communication, defaults to **"127.0.0.1"** if communicating locally.
   - :code:`Config_Agen_Num_Port` : Configures the socket communication port, which is used to communicate with the algorithm end to determine the number of trackers (agents) to be set.
   - :code:`Train_Total_Steps` : The maximum number of training steps. If the steps exceed this number, the simulation returns done.
   - :code:`Init_No_Done_Steps` : The number of simulation steps without done status during initialization. This prevents the unstable physical properties of the tracker during initialization from triggering the done status. This parameter should be set to a reasonable value.
   - :code:`No_Reward_Done_Steps` : The number of simulation steps that result in a done status when the reward is continuously zero, which helps improve training efficiency.
   - :code:`Control_Frequence` : The control frequency for the control algorithm. During training, the simulation end executes at a fixed control frequency of 500Hz based on the simulation time. This parameter is used to adjust the average control frequency of the algorithm end.

   * :code:`Customized_Rewards`: Whether to enable the customized reward parameter. Users can calculate rewards based on the customized reward parameter.

      * For more details on the customized reward parameter, see: :ref:`Customized Parameter Interface`
   * :code:`Lidar_Enable`: Whether to enable lidar point cloud data.

      * For more details on lidar point cloud data, see: :ref:`Customized Parameter Interface`
   * :code:`Tracking_Object`: The tracked object setting (default is SUMO_VEHICLE). Example tracking objects include "SUMO_VEHICLE", "Pedestrian", "Shrimp", "Create", "Sojourner", "Mantis", etc. Custom tracking objects are also supported. See the project manual.

      * For detailed descriptions of tracking object types, see: :ref:`Tracked Objects`

   * :code:`Verbose`: Enable log recording. If set to true, some important parameters will be printed in the Webots terminal window for users to observe. Additionally, program run logs will be generated in the :code:`Webots_Simulation/traffic_project/logs` folder, mainly for debugging the simulation environment.

      .. image:: ../_static/image/WebotsLogOutput.png
         :alt: webots日志输出（“train”&“video”）
         :width: 500px
         :align: center

      * :code:`id` : The name of the tracker.
      * :code:`done` : Whether to return done.
      * :code:`reward` : The current reward size.
      * :code:`count` : The step count of steps.
      * :code:`time` : Simulation time.
      * :code:`carDir` : The movement direction of the tracked target.
      * :code:`pitchAngle` : The pitch axis angle of the camera.
      * :code:`doneState` : The reason for generating done, including "height" (unreasonable tracker height), "distance" (the error between the tracker's target position and the actual position is too large), "velocity" (unreasonable tracker movement speed), "yaw velocity" (unreasonable tracker rotational speed around the vertical axis), "pitch or yaw angle" (unreasonable tracker attitude).

Tracker (only effective for drones) generates a physical range parameter configuration of done
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: json

   "Done_Range": {
        "max_height": 50,
        "min_height": 2,
        "velocity": 100,
        "omiga": 6.283,
        "roll": 1.22,
        "pitch": 1.22,
        "distance_error": 50
   }

**Parameter Description**

   - :code:`max_height` ：Tracker maximum flight altitude (:math:`m`).
   - :code:`min_height` ：Tracker minimum flight altitude (:math:`m`).
   - :code:`velocity` ：Tracker maximum flight velocity (:math:`m/s`).
   - :code:`omiga` ：Tracker maximum angular velocity (:math:`rad/s`).
   - :code:`roll` ：Tracker maximum roll angle (:math:`rad`).
   - :code:`pitch` ：Tracker maximum pitch angle (:math:`rad`).
   - :code:`distance_error` ：Maximum error between the tracker's desired position and current position (:math:`m`).

.. _Built-in reward parameter configuration:

Built-in reward parameter configuration (valid for drones only, cars return reward=1 by default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: json

   "Reward_Config": {
        "reward_type": "view",
        "reward_mode": "continuous",
        "reward_cut_off": 0.001,
        "distance_scale": 0.01,
        "distance_range": 7,
        "view_scale": 4,
        "view_range": 0.7
   }

**Parameter Description**

   - :code:`reward_type` : The type of reward (default is view). "View" detects based on the quadrilateral projected onto the ground from the camera's perspective, while "distance" detects based on the distance from the midpoint projection in the camera's view to the target.
   - :code:`reward_mode` : The default mode of reward. "Continuous" produces a continuous floating-point number between [0, 1], while "discrete" produces an integer of 0 or 1.
   - :code:`reward_cut_off` : Reward cut-off. When the obtained reward is less than this value, :code:`No_Reward_Done_Steps` starts counting.
   - :code:`distance_scale` : Distance scale (default is continuous). This parameter is only effective in continuous mode and controls the decay rate of the reward due to distance error.
   - :code:`distance_range` : The distance error range for generating rewards.

   * :code:`view_scale` : View scale. This parameter is only effective in continuous mode and view type, controlling the decay rate of the reward due to deviation from the view center.
      
      * For specific parameter meanings, see: :ref:`Built-in Reward`
   
   - :code:`view_range` : The view range for generating rewards. This parameter is used to scale the quadrilateral used for reward calculation, i.e., the size of the quadrilateral box in the camera view. Generally, the range is set to [0,1].

SUMO Traffic System Parameter Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: json

   "Sumo_Params": {
        "rou_update": false,
        "max_sumo_car": 40,
        "fixed_car_group_num": true,
        "car_group_num": 5,
        "car_import_interval": 52.0,
        "car_type": "passenger",
        "fixed_color": false,
        "normalize_color": [1,0,0],
        "max_car_speed": 20,
        "max_car_accel": 25,
        "max_car_decel": 25,
        "max_rou_distance": 7000,
        "min_rou_distance": 500,
        "route_num": 100000,
        "fixed_seed": false,
        "random_seed": 1
   }

**Parameter Description**

   - :code:`rou_update` : Whether the traffic simulation route file is updated. If you want to obtain a specific route, set it to false. **Note:** Any change in the parameters of this module will cause the route to refresh automatically.
   - :code:`max_sumo_car` : Maximum number of vehicles in the map.
   - :code:`fixed_car_group_num` : Whether to customize the number of vehicles added to the environment in each group.
   - :code:`car_group_num` : Custom number of vehicles added to the environment in each group. **Note:** In training and video mode, if this parameter is set unreasonably (< Agent number * 3), the system will automatically set a reasonable parameter (= Agent number * 3), otherwise the environment cannot run stably.
   - :code:`car_import_interval` : The interval time (s) between each group of vehicles added to the map.

   * :code:`car_type` : The type of vehicle (default is passenger), including "passenger", "bus", "truck", "trailer", "motorcycle".

      * All supported vehicle types can be found at: :ref:`SUMO_VEHICLE`

   - :code:`fixed_color` : Whether to fix the vehicle color.
   - :code:`normalize_color` : Normalized RGB color vector.
   - :code:`max_car_speed` : Maximum vehicle speed (:math:`m/s`).
   - :code:`max_car_accel` : Maximum vehicle acceleration (:math:`m/s^2`).
   - :code:`max_car_decel` : Maximum vehicle deceleration (:math:`m/s^2`).
   - :code:`max_rou_distance` : Maximum route length (:math:`m`).
   - :code:`min_rou_distance` : Minimum route length (:math:`m`).
   - :code:`route_num` : Maximum number of routes (note that this is the maximum, :code:`obj_edge_distribution_multilateral` may actually have fewer routes than the set parameter due to the randomization process).
   - :code:`fixed_seed` : Whether to use a fixed random seed. If you want to obtain stable routes and vehicle styles, set it to true.
   - :code:`random_seed` : The fixed random seed.

Other object tracking parameter configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Only effective when :code:`Tracking_Object` is not "SUMO_VEHICLE".

.. code:: json

   "Other_Params": {
        "max_obj_num": 10,
        "obj_import_interval": 0.5,
        "import_group_num": 4,
        "obj_edge_distribution_random": false,
        "obj_edge_distribution_multilateral": false,
        "obj_edge_distribution_fixed": 0,
        "obj_edge_distribution_max":10,
        "obj_edge_distribution_min":-10
   }

**Parameter Description**

   - :code:`max_obj_num` ：Maximum number of objects.
   - :code:`obj_import_interval` ：Time interval (s) for adding each group of objects to the map.
   - :code:`import_group_num` ：Number of objects added per group.
   - :code:`obj_edge_distribution_random` ：Whether to enable random distribution of objects along the sides of the map roads. If true, objects will be randomly placed in a random direction at random positions on a random path. If false, objects will be placed at a fixed distance in the vertical direction at random positions on a random path.
   - :code:`obj_edge_distribution_multilateral` ：Whether to enable bilateral distribution. If true, the distribution range will be :code:`[min, max] ∪ [-max, -min]` . If false, the distribution range will be :code:`[min, max]` .
   - :code:`obj_edge_distribution_fixed` ：Fixed distance (:math:`m`) from the center of the road.
   - :code:`obj_edge_distribution_max` ：Maximum distance (:math:`m`) from the center of the road.
   - :code:`obj_edge_distribution_min` ：Minimum distance (:math:`m`) from the center of the road.

Output video parameter configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Effective only when :code:`Simulation_Mode` is not “video”.

.. code:: json

   "Out_Video": {
        "channels": 4,
        "fps": 50.0,
        "start_time": 1.0,
        "total_time": 50.0,
        "warm_up_steps": 30,
        "output_car_dir": false,
        "random_action": true,
        "forward_speed":40,
        "backward_speed":-40,
        "left_speed":40,
        "right_speed":-40,
        "cw_omega":2,
        "ccw_omega":-2
   }

**Parameter Description**

   - :code:`channels` ：Number of video channels, which corresponds to the number of trackers in the imported map.
   - :code:`fps` ：Frames per second calculated based on simulation time (video frames are exported at this frame rate).
   - :code:`start_time` ：Simulation time (:math:`s`) at which video export begins.
   - :code:`total_time` ：Duration of the video in simulation time (:math:`s`).
   - :code:`warm_up_steps` ：The number of steps after reset during which no data is output. Note that each step has a cycle of 2ms.
   - :code:`output_car_dir` ：Whether to output the vehicle direction. If enabled, only the vehicle movement direction is output; otherwise, reward and action are output (Vehicle directions: 0 stop, 1 forward, 2 left turn, 3 right turn).
   - :code:`random_action` ：Whether the tracker uses random actions. If enabled, random actions are output based on Control_Frequency. Otherwise, the tracker will precisely follow the vehicle, and the action output will be -1 (meaningless).
   - :code:`forward_speed` ：Forward speed of the tracker’s random action (:math:`m/s`).
   - :code:`backward_speed` ：Backward speed of the tracker’s random action (:math:`m/s`).
   - :code:`left_speed` ：Leftward speed of the tracker’s random action (:math:`m/s`).
   - :code:`right_speed` ：Rightward speed of the tracker’s random action (:math:`m/s`).
   - :code:`cw_omega` ：Clockwise rotation speed of the tracker’s random action (:math:`rad/s`).
   - :code:`ccw_omega` ：Counterclockwise rotation speed of the tracker’s random action (:math:`rad/s`).

Tracker Control Parameter Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   This set of parameters is used to randomize the tracking properties of the tracker itself.

.. code:: json

   "Drone_Random_Config": {
        "start_time_bias_ms": 310,

        "view_pitch_random": false,
        "view_pitch_fixed": 1,
        "view_pitch_random_max": 1.57,
        "view_pitch_random_min": 0.7,

        "height_random": true,
        "height_fixed": 15.0,
        "height_random_max": 25.0,
        "height_random_min": 13.0,

        "direction_random": false,
        "direction_random_multilateral": false,
        "direction_fixed": 0,
        "direction_random_max": 0.1,
        "direction_random_min": -0.1,

        "horizon_bias_random": false,
        "horizon_bias_multilateral": true,
        "horizon_bias_fixed": 0,
        "horizon_bias_random_max": 3,
        "horizon_bias_random_min": 0.1,

        "verticle_bias_random": false,
        "verticle_bias_multilateral": true,
        "verticle_bias_fixed": 0,
        "verticle_bias_random_max": 3,
        "verticle_bias_random_min": 0.1
   }

**Parameter Description**

   * :code:`start_time_bias_ms` : Due to the time required for environment initialization, theoretically, the more agents are set, the longer the initialization time. This parameter can adjust the overall initialization time.

      * **Note: The total initialization time will increase with the number of agents set, and it will be longer than the time set by this parameter.**

   - :code:`view_pitch_random` : Randomization of the tracker camera pitch angle.

   * :code:`view_pitch_fixed` : If the above parameter is false, the angle defined by this parameter will be used.

      * If the angle is greater than 0, it is a downward pitch; otherwise, it is an upward pitch.
      * In practical usage, a downward pitch is common. Therefore, the parameter range in the simulation environment is limited to :math:`[0.5, 1.57](rad)`.

   - :code:`view_pitch_random_max` : Maximum camera downward pitch.
   - :code:`view_pitch_random_min` : Minimum camera downward pitch.
   - :code:`height_random` : Randomization of tracker flight height. Other parameter meanings are the same as above.
   - :code:`direction_random` : Randomization of the tracker’s initial view direction following the object, with a range of :math:`[-pi,pi](rad)`.

   * :code:`direction_random_multilateral` : Whether to enable bilateral randomization configuration.

      * :code:`false`, :math:`[min, max]` ; :code:`true`, :math:`[-max, -min] ∪ [min, max]`

   - :code:`horizon_bias_random` : Horizontal offset of the initial view tracker tracking object. If the subsequent parameter is positive, the object shifts to the left; if negative, the object shifts to the right. Other parameters are the same as above.
   - :code:`verticle_bias_random` : Vertical offset of the initial view tracker tracking object. If the subsequent parameter is positive, the object shifts upward; if negative, the object shifts downward. Other parameters are the same as above.

Simulation Environment Parameter Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   This set of parameters is used to randomize the tracking attributes of the tracker itself.

.. code:: json

    "Env_Params": {
        "background_luminosity_random": false,
        "bgl_incremental": 0,
        "bgl_random_max": 1,
        "bgl_random_min": 0,
        "backgroundLight_luminosity_random": false,
        "bgLl_incremental": 0,
        "bgLl_random_max": 1,
        "bgLl_random_min": 0,
        "foggy_use_default": true,
        "foggy_visibility_range_random": false,
        "foggy_visibility_range_fixed": 400,
        "foggy_visibility_range_max": 1000,
        "foggy_visibility_range_min": 300
    }

**Parameter Description**

   * :code:`background_luminosity_random`: Whether to randomize the environmental background luminosity.

   * :code:`bgl_incremental`: If the above parameter is :code:`false`, use this parameter to define a fixed environmental luminosity.

   - :code:`bgl_random_max`: Maximum environmental background luminosity.

   - :code:`bgl_random_min`: Minimum environmental background luminosity.

   * :code:`backgroundLight_luminosity_random`: Whether to randomize the environmental background light luminosity.

   - :code:`bgLl_incremental`: If the above parameter is :code:`false`, use this parameter to define a fixed environmental background light luminosity.

   - :code:`bgLl_random_max`: Maximum environmental background light luminosity.

   - :code:`bgLl_random_min`: Minimum environmental background light luminosity.

   * :code:`foggy_use_default`: Whether to enable environmental fog.

   * :code:`foggy_visibility_range_random`: Whether to randomize the visibility range of environmental fog.

   - :code:`foggy_visibility_range_fixed`: If the above parameter is :code:`false`, use this parameter to define a fixed visibility range for environmental fog.

   - :code:`foggy_visibility_range_max`: Maximum visibility range of environmental fog.

   - :code:`foggy_visibility_range_min`: Minimum visibility range of environmental fog.

Configuration Parameter Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   For recommendations on simulator parameter configurations, please refer to the document: :doc:`Parameters`.


.. _Tracked Objects:

Tracked Objects
--------------------

   .. raw:: html

      <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
            This project provides 18 types of 24 predefined tracking targets, and offers a plug-and-play interface that supports users in utilizing self-designed models and controllers.
      </div>

.. _SUMO_VEHICLE:

SUMO_VEHICLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   SUMO_VEHICLE is controlled by the SUMO traffic management system to manage the traffic conditions on the map, allowing vehicles to follow planned routes on the map. The type of vehicle can be specified.

**passenger**

   Passenger cars include common sedans, SUVs, and business vehicles, as shown below:

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 25%;">
            <img src="../_static/image/BMWX5.png" alt="Image 1" style="width: 90%;" />
            <figcaption>BmwX5</figcaption>
         </figure>
         <figure style="text-align: center; width: 25%;">
            <img src="../_static/image/CITROENCZero.png" alt="Image 2" style="width: 90%;" />
            <figcaption>CitroenCZero</figcaption>
         </figure>
         <figure style="text-align: center; width: 25%;">
            <img src="../_static/image/LINKOLNMKZ.png" alt="Image 2" style="width: 90%;" />
            <figcaption>LinkolnMKZ</figcaption>
         </figure>
         <figure style="text-align: center; width: 25%;">
            <img src="../_static/image/MERCEDESBENZSprinter.png" alt="Image 2" style="width: 90%;" />
            <figcaption>MercedesBenzSprinter</figcaption>
         </figure>
      </div>

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/RANGEROVERSportSVR.png" alt="Image 1" style="width: 90%;" />
            <figcaption>RangeRoverSportSVR</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/TESLAModel3.png" alt="Image 2" style="width: 90%;" />
            <figcaption>TeslaModel3</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/TOYOTAPrius.png" alt="Image 2" style="width: 90%;" />
            <figcaption>ToyotaPrius</figcaption>
         </figure>
      </div>

.. .. figure:: ../_static/image/BMWX5.png
..    :alt: BMWX5
..    :width: 500px
..    :align: center

..    BmwX5

.. .. figure:: ../_static/image/CITROENCZero.png
..    :alt: CITROENCZero
..    :width: 500px
..    :align: center

..    CitroenCZero

.. .. figure:: ../_static/image/LINKOLNMKZ.png
..    :alt: LINKOLNMKZ
..    :width: 500px
..    :align: center

..    LinkolnMKZ

.. .. figure:: ../_static/image/MERCEDESBENZSprinter.png
..    :alt: MERCEDESBENZSprinter
..    :width: 500px
..    :align: center

..    MercedesBenzSprinter

.. .. figure:: ../_static/image/RANGEROVERSportSVR.png
..    :alt: RANGEROVERSportSVR
..    :width: 500px
..    :align: center

..    RangeRoverSportSVR

.. .. figure:: ../_static/image/TESLAModel3.png
..    :alt: TESLAModel3
..    :width: 500px
..    :align: center

..    TeslaModel3

.. .. figure:: ../_static/image/TOYOTAPrius.png
..    :alt: TOYOTAPrius
..    :width: 500px
..    :align: center

..    ToyotaPrius

**bus**

   Unified model, large passenger vehicles

.. figure:: ../_static/image/BUS.png
   :alt: BUS
   :width: 500px
   :align: center

   Bus

**truck**

   Unified vehicle type, truck without cargo box

.. figure:: ../_static/image/TRUCK.png
   :alt: TRUCK
   :width: 500px
   :align: center

   Truck

**trailer**

   Unified model, truck with cargo box

.. figure:: ../_static/image/TRAILER.png
   :alt: TRAILER
   :width: 500px
   :align: center

   Trailer

motorcycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Two types of vehicles, motorcycles

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 50%;">
            <img src="../_static/image/SCOOTER.png" alt="SCOOTER" style="width: 90%;" />
            <figcaption>Scooter</figcaption>
         </figure>
         <figure style="text-align: center; width: 50%;">
            <img src="../_static/image/MOTORBIKE.png" alt="MOTORBIKE" style="width: 90%;" />
            <figcaption>Motorbike</figcaption>
         </figure>
      </div>


Pedestrian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Pedestrian objects will move along a certain path at a certain speed, and the human body will simulate real human gait during motion.

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/PEDESTRIAN.png" alt="PEDESTRIAN " style="width: 90%;" />
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/PEDESTRIAN2.png" alt="PEDESTRIAN2" style="width: 90%;" />
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/PEDESTRIAN3.png" alt="PEDESTRIAN3" style="width: 90%;" />
         </figure>
      </div>
      <p style="text-align: center;">Pedestrian</p>


Wheel Robots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   Wheel Robots

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/SHRIMP.png" alt="SHRIMP" style="width: 90%;" />
            <figcaption>Shrimp</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/CREATE.png" alt="CREATE" style="width: 90%;" />
            <figcaption>Create</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/SOJOURNER.png" alt="SOJOURNER" style="width: 90%;" />
            <figcaption>Sojourner Rover</figcaption>
         </figure>
      </div>

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 50%;">
            <img src="../_static/image/BB_8.png" alt="BB_8" style="width: 90%;" />
            <figcaption>BB-8 Spherical Robot</figcaption>
         </figure>
         <figure style="text-align: center; width: 50%;">
            <img src="../_static/image/FIREBIRD6.png" alt="FIREBIRD6" style="width: 90%;" />
            <figcaption>FireBird6</figcaption>
         </figure>
      </div>


Legged Robots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/MANTIS.png" alt="MANTIS" style="width: 90%;" />
            <figcaption>Mantis Large Hexapod Robot</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/AIBOERS7.png" alt="AIBOERS7" style="width: 90%;" />
            <figcaption>AiboErs7 Quadruped Robot</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/BIOLOIDDOG.png" alt="BIOLOIDDOG" style="width: 90%;" />
            <figcaption>BioloidDog Quadruped Robot</figcaption>
         </figure>
      </div>

   .. raw:: html

      <div style="display: flex; align-items: center; justify-content: space-between;">
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/SCOUT.png" alt="SCOUT" style="width: 90%;" />
            <figcaption>Scout Bipedal Robot</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/GHOSTDOG2.png" alt="GHOSTDOG2" style="width: 90%;" />
            <figcaption>GhostDog Quadruped Robot</figcaption>
         </figure>
         <figure style="text-align: center; width: 33%;">
            <img src="../_static/image/HOAP2.png" alt="HOAP2" style="width: 90%;" />
            <figcaption>Hoap2 Bipedal Robot</figcaption>
         </figure>
      </div>



Custom Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   This project supports custom tracked objects, and the steps are as follows:

      1. Create a proto file for Webots following `webots wiki <https://cyberbotics.com/doc/reference/proto#:~:text=Webots%20Reference%20Manual.%20R2023b.%20PROTO.>`_ . The attributes that must be exposed to the scene tree include "translation", "rotation", and "name". The description file should be stored in :code:`UAV_Follow_Env/Webots_Simulation/traffic_project/protos`

      .. figure:: ../_static/image/SceneTreePropertyPack.png
         :alt: 场景树属性包
         :width: 600px
         :align: center

         Scenario Tree Attribute Pack

      2. You can choose to write a controller to give the tracked object autonomous behavior.
      3. Load the established proto file in the :code:`IMPORTABLE EXTERNPROTO` module of webots.

      .. raw:: html

         <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="text-align: center; width: 38%;">
               <img src="../_static/image/IMPORT_PROTO.png" alt="IMPORT_PROTO" style="width: 90%;" />
            </div>
            <div style="text-align: center; width: 62%;">
               <img src="../_static/image/IMPORT_PROTO2.png" alt="IMPORT_PROTO2" style="width: 90%;" />
            </div>
         </div>

         <p style="text-align: center; ">
            IMPORT PROTO
         </p>

      4. Write the name of the proto into the safety check file :code:`UAV_Follow_Env/Webots_Simulation/traffic_project/config/safetyCheck.py`

         .. figure:: ../_static/image/SafeCheck.png
            :alt: SafeCheck
            :width: 600px
            :align: center

            Security Check

      5. Modify the description of :code:`Tracking_Object` in the json configuration file so that its description matches the proto name.
      6. After the above steps, you can use the tracker to track custom objects.

.. _built-in Reward:

Built-in Reward
--------------------

   .. raw:: html

      <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
            This project provides both <b>discrete and continuous</b> reward functions, which can be used to design different agent evaluation metrics.
      </div>
      </br>

Reward Function
~~~~~~~~~~~~~~~~~~~~

   .. raw:: html

      <div style="border-left: 4px solid #FFC1C1; padding-left: 10px; margin-left: 0;">
        Due to the existence of the super intelligent agent in Webots, we can obtain the coordinates of the aircraft and the tracked car at each moment, (x_f, y_f, z_f) and (x_v, y_v, z_v), and directly determine whether the tracking is successful based on the actual pitch angle of the camera and the set camera FOV.
      </div>
      </br>

   For the tracker (drone), there are two options for the reward function. The first option is sparse rewards, where rewards are given when the tracked object enters the tracking range, and no rewards are given when it leaves the range (the reward is 0). The mathematical expression is as follows:

   .. math::

      r_{d} = \begin{cases}
      1 & t \in I, \\
      0 & \text{otherwise}.
      \end{cases}

   Where :math:`I` represents the tracking range (the area captured by the camera lens), and :math:`t` represents the position of the tracked object within the tracking range (the area captured by the camera lens).

   .. _Discrete Reward Diagram for Tracking Object:

   .. figure:: ../_static/image/Discrete_reward.png
      :alt: Discrete_reward
      :width: 600px
      :align: center

      Discrete Reward Diagram of the Tracking Object

   The second type is dense reward, which gives a reward that decreases as the distance increases by evaluating the position of the tracking object relative to the center of the tracking range. The higher the reward, the closer the target is to the center point of the range, and vice versa.

   .. _Continuous Reward Diagram for Tracking Object:

   .. _figcontr:

   .. _Dense reward calculation formula:

   .. figure:: ../_static/image/Continuous_reward.png
      :alt: Continuous_reward
      :width: 600px
      :align: center

      Continuous Reward Diagram for Object Tracking


   The figure above is a schematic of a tracking object within the camera frame, note that

   .. math::

      x = \frac{\mid p_{vc}- I_{OG}\mid}{\mid E_{G_c}- I_{OG}\mid}

   Then, the dense reward can be obtained using the following expression:

   .. math::

      r_{c} = \begin{cases}
      \tanh\left(\alpha(1-x)^{3}\right), & t \in I_{clip}, \\
      0 & \text{otherwise}.
      \end{cases}

   The closer the target is to the center of the range, the closer the reward is to 1; conversely, the farther away, the closer the reward is to 0. :math:`\alpha` is a constant, and a recommended value is between 3 and 5.
   In addition, :math:`I_{clip}` is the effective reward determination range (as shown in the red box in the figure above :ref:`figcontr`), and the ratio of its side length :math:`W_{I_{clip}}` to the original image side length :math:`W_{I}` can be expressed by :math:`\lambda_{clip}` as follows.

   .. math::

      \lambda_{clip} = \frac{W_{I_clip}}{W_{I}}

   According to the above definition, the reasonable range of :math:`\lambda_{clip}` is :math:`[0,1]`, and in actual training, it is recommended to set the parameter as :math:`\lambda_{clip}=0.7`.

Reward Judgment
~~~~~~~~~~~~~~~~~~~~

   The acquisition of the above reward function is based on the judgment of the tracked object's position. In practice, the position of the tracked object in the camera image can be provided through machine vision recognition or manual annotation. However, in simulation training, in order to simplify the calculation and speed up the algorithm, we directly use the coordinates of the tracked object to determine whether it has entered the tracking range.

   .. _奖励获取示意图:

   .. figure:: ../_static/image/Reward.png
      :alt: Reward
      :width: 600px
      :align: center

      Schematic diagram of reward acquisition

Principle
^^^^^^^^^^^^^^^^^^^^

   First, the camera focal length in the simulation needs to be obtained, and the expression is calculated as follows:

   .. math::

      f = \frac{W}{2\tan\left(\frac{1}{2}FoV\right)}

   Where :math:`W` represents the width of the camera image (in pixels), and :math:`FoV` refers to the field of view of the tracker camera, as shown in Figure b of the :ref:`奖励获取示意图` (a).

   Then, as shown in the :ref:`奖励获取示意图` (a), we need to project the camera's corner points onto the spatial plane where the tracked object is located. Next, as shown in the :ref:`奖励获取示意图` (b), determine the coordinates of the tracked object. Finally, by establishing the camera coordinate system :math:`\{c\}` at the optical center of the camera, the coordinates of the four corners of the camera image in the coordinate system :math:`\{c\}` can be obtained:

   .. math::

      LU\left(-f,-\frac{1}{2}W,\frac{1}{2}H\right),\\
      LD\left(-f,-\frac{1}{2}W,-\frac{1}{2}H\right),\\
      RU\left(-f,\frac{1}{2}W,\frac{1}{2}H\right),\\
      RD\left(-f,\frac{1}{2}W,-\frac{1}{2}H\right)

   By associating with the optical center :math:`C` :math:`(0,0,0)`, we can obtain four linear equations:

   .. math::

      \begin{matrix}
      l_{LUC}: \frac{x}{-f} = \frac{2y}{-W} = \frac{2z}{H}, \\
      l_{LDC}: \frac{x}{-f} = \frac{2y}{-W} = \frac{2z}{-H}, \\
      l_{RUC}: \frac{x}{-f} = \frac{2y}{W} = \frac{2z}{H}, \\
      l_{RDC}: \frac{x}{-f} = \frac{2y}{W} = \frac{2z}{-H}
      \end{matrix}

   Then get the equation for the ground (horizontal):

   .. math::

      G_{w}: z = h

   :math:`\{w\}` represents the world coordinate system, and :math:`h` is the ground height.

   Since the pose of the tracker gimbal is known, it is easy to obtain the transformation relationship from the camera coordinate system :math:`\{c\}` to the world coordinate system :math:`\{w\}`, which is the homogeneous transformation matrix :math:`T_{ct}`.

   By transforming the plane equation :math:`G_{w}` to the coordinate system :math:`\{c\}`, and solving it together with the four line equations, the four ground intersection points :math:`LU_{G}, LD_{G}, RU_{G}, RD_{G}` can be obtained. These four points form the four corner points of the tracking range :math:`I`, thus determining the tracking area :math:`I`.

   Finally, read the tracking object's coordinate point :math:`p_{vG}` from the simulation environment, and convert it along with the image center point :code:`I_{OG}` to the coordinate system :math:`\{c\}`, obtaining :math:`p_{vc}`. Using the car's coordinates :math:`p_{vc}`, the four intersection points (:code:`LU_G`, :code:`LD_G`, :code:`RU_G`, and :code:`RD_G`), and the image center :code:`I_{OG}`, by utilizing the :ref:`Dense reward calculation formula` , the ratio :math:`x` can be calculated. When :math:`0 \leq x \leq 1`, the object is within the image, indicating successful tracking.

   The calculation method is similar when the ground is not horizontal.


Projection Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   After implementing the above principle, the effect is as shown in the following video. By placing the block at the intersection point of the ground and the calculated line in the simulation, the camera's view range can be seen in real time:

   .. raw:: html

      <video width="640" height="360" controls>
         <source src="../_static/video/GetReward_Video.mp4" type="video/mp4">
         Your browser does not support the video tag.
      </video>

   .. raw:: html

      <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
         Note: The upper limit of the field of view cannot exceed the horizon, otherwise the calculation results will be meaningless.
      </div>

.. raw:: html

   </br>


.. _Customized Parameter Interface:

Customized Parameter Interface
----------------------------------------

.. raw:: html

   <div style="background-color: #e5f3e5; padding: 15px; border-radius: 5px; border: 2px solid #66CD00;">
         This project provides common <b>6 types of sensor data</b>, which can be used for subsequent multi-sensor collaborative task design.
   </div>
   </br>

Input Actions
~~~~~~~~~~~~~~~~~~~~

   The input actions are used to control the movement of the tracker. Currently, the tracker has four actions: move forward, move backward, move left, move right, plus the reset data, totaling 5 floating-point numbers.

Return Parameters
~~~~~~~~~~~~~~~~~~~~

   The return parameters mainly include three parts: the basic data packet, the custom reward data packet, and the radar data packet.

**Basic Data Packet**

   The basic data packet consists of 22 floating-point numbers, as shown below:

   .. code:: c++

      typedef struct _Odometry{
        double t;// simulation steps (not simulation time)
        vector3 position;// three-axis position m
        vector3 linear;// three-axis linear velocity m/s
        vector3 acc;// three-axis acceleration m/s^2
        vector3 angular;// three-axis angular velocity rad
        vector4 orientation;// quaternion
        vector3 angle;// Euler angles
        double reward;// reward
        double done;// whether simulation ends
      }Odometry;


.. raw:: html

   <html>

   <head>

       <style>


           table {

               border-collapse: collapse;

               width: 100%; /* 根据需要设置宽度 */

           }


           th {

               border-top: 2px solid black; /* 或者使用你想要的任何颜色和粗细 */

               border-bottom: 2px solid black; /* 底部边框，如果需要的话 */

               padding: 8px; /* 设置内边距以改善可读性 */

           }


           td {

               padding: 6px; /* 设置内边距以改善可读性 */

           }


           td, th {

               border-left: none;

               border-right: none;

           }


           .vision-row {

               background-color: #FFC1C1;

           }



           .motion-row {

               background-color: #87CEEB;

           }


           .row-line {

               border-bottom: 2px solid black; /* 底部边框，如果需要的话 */

           }

           .merged-cell {
               text-align: center; /* 水平居中 */
               vertical-align: middle; /* 垂直居中，虽然对于td来说这通常是默认的 */
           }

       </style>

   </head>

   <body>

   <table>
    <tr class="merged-cell">
        <th>Category</th>
        <th>Sensor</th>
        <th>Parameter</th>
        <th>Type</th>
        <th>Description</th>
        <th>Potential Tasks</th>
    </tr>
    <tr class="merged-cell">
        <td rowspan="2" class="vision-row merged-cell">Vision</td>
        <td>Camera</td>
        <td>Image</td>
        <td>Mat</td>
        <td>Images captured by the camera</td>
        <td>Default sensor</td>
    </tr>
    <tr class="row-line merged-cell">
        <td>Lidar</td>
        <td>LidarCloud</td>
        <td>vector2000</td>
        <td>Point cloud from RpLidarA2(m)</td>
        <td>Obstacle avoidance</td>
    </tr>
    <tr class="merged-cell">
        <td rowspan="6" class="motion-row merged-cell">Motion</td>
        <td rowspan="2" class="merged-cell">GPS</td>
        <td>Position</td>
        <td>vector3</td>
        <td>Position (m)</td>
        <td>Visual navigation</td>
    </tr>
    <tr class="merged-cell">
        <td>Linear</td>
        <td>vector3</td>
        <td>Linear velocity (m/s)</td>
        <td>Visual navigation</td>
    </tr>
    <tr class="merged-cell">
        <td>Accelerometer</td>
        <td>Acc</td>
        <td>vector3</td>
        <td>Acceleration (m/s^2)</td>
        <td>Visual navigation</td>
    </tr>
    <tr class="merged-cell">
        <td>Gyroscope</td>
        <td>Angular</td>
        <td>vector3</td>
        <td>Angular velocity (rad/s)</td>
        <td>Robot posture stabilization</td>
    </tr>
    <tr class="merged-cell">
        <td rowspan="2" class="merged-cell">IMU</td>
        <td>Angle</td>
        <td>vector3</td>
        <td>Eular angles (rad)</td>
        <td>Robot posture stabilization</td>
    </tr>
    <tr class="row-line merged-cell">
        <td>Orientation</td>
        <td>vector4</td>
        <td>Quaternion representation</td>
        <td>Robot posture stabilization</td>
    </tr>
   </table>
   </body>
   </html>
   </br>


**Custom Reward Data Packet**

   The custom reward data packet consists of 59 floating point numbers + 1 string, including the following parts

   .. code:: c++
      
      typedef struct _rewardData{
        double cameraWidth;// Image width (pixels)
        double cameraHeight;// Image height (pixels)
        double cameraFov;// Camera field of view (rad) [0,pi]
        double cameraF;// Camera focal length estimate (pixels)
        double cameraPitch;// Camera pitch angle (rad)
        double trackerHeight;// Tracker height (m)
        double T_ct[16];// Homogeneous transformation matrix from camera to world coordinate system
        double T_tw[16];// Homogeneous transformation matrix from vehicle to world coordinate system
        vector3 cameraMidGlobalPos;// 3D coordinates of the camera center mapped to the ground in the world coordinate system
        vector3 carMidGlobalPos;// 3D coordinates of the vehicle center in the world coordinate system
        vector3 cameraMidPos; // Camera center coordinates in the world coordinate system
        vector4 carDronePosOri; // 1D pose + 3D coordinates of the vehicle center in the tracker coordinate system (the first element is the pose)
        vector3 carDroneVel; // 3D velocity of the vehicle center in the drone coordinate system
        vector3 carDroneAcc; // 3D acceleration of the vehicle center in the drone coordinate system
        double crash; // Whether the tracker has collided with a building
        double carDir;// Vehicle running direction (0 stop, 1 straight, 2 left turn, 3 right turn)
        std::string carTypename;// Object type
      }rewardData;

   - Among them, the parameter :code:`carCameraPosOri` defines the tracker coordinate system and pose angles as follows:
   
   .. figure:: ../_static/image/DroneCoordinates.png
      :alt: 无人机坐标系                                  
      :width: 250px                                              
      :align: center

      Definition of Drone Coordinate System


**Radar Data Packet**

   Radar point cloud data. The tracker in this environment is equipped with RpLidarA2 single-line radar, and its point cloud data will output an array with a length of 2000.

