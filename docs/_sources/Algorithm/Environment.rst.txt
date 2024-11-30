Environment Wrapping
==============================

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
                window.location.href = '../../zh/Algorithm/Environment.html';
            } else if (lang === 'en') {
                window.location.href = '../../en/Algorithm/Environment.html';
            }
        }
    </script>
    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

This project provides three forms of Environment (Path: :code:`Alg_Base/rl_a3c_pytorch_benchmark/envs`): the base Environment class :code:`BenchEnv_Multi()`, the Environment class wrapped by OpenAI Gym (Gynasium) :code:`gym()`:code:`gynasium()`, and our own implementation of the parallel Environment class.

The relationships among these three Environment types are shown in the figure below:

.. figure:: ../_static/image/Environment3Types.png
  :alt: Relationship diagram of three types of environment classes
  :width: 600px
  :align: center

  Diagram of the three environment classes


.. _BenchEnv_Multi:
    
1 Base Environment Class
-------------------------------------

Part 1 Interface Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. raw:: html

      <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
            The base environment class is the <b>class for direct communication between the algorithm side and the simulator side</b>, mainly responsible for multi-process communication and data transmission with the simulator.
            If you only need to call the class for testing, you can directly jump to: <a href="#config">configuration file</a> and <a href="#makeenv">constructor</a>
      </div>
      </br>

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/environment.py</code> in <code>BenchEnv_Multi()</code>
        </div>
        </br>


    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            1. <code>__init__</code>: Used to initialize the communication interface, number of processes, and other essential parameters for the environment.
      </div>
      </br>

    * :code:`Action_dim(int)`: Agent action dimension
    * :code:`action_list(list)`: Used to convert discrete action commands into continuous movement commands

      * The storage order of :code:`action_list` is: :code:`[Forward, Backward, Left, Right, CCW, CW]`, representing the movement commands "forward, backward, left, right, counterclockwise, clockwise."

    * :code:`process_state(function)`: Function for post-processing the images
    * :code:`arg_worker(int)`: System parallelism count
    * :code:`process_idx(int)`: Current environment's parallel index
    * :code:`Other_State(bool)`: Whether to enable additional state options on the simulator side: :code:`Other_State`, detail see: :ref:`Parameter configuration of the simulation environment`
    * :code:`CloudPoint(bool)`: Whether to enable the point cloud option on the simulator side: :code:`CloudPoint`, detail see: :ref:`Parameter configuration of the simulation environment`
    * :code:`RewardParams(bool)`: Whether to enable additional reward parameters options on the simulator side: :code:`RewardParams`, detail see: :ref:`Parameter configuration of the simulation environment`
    * :code:`port_process(int)`: Port specified for data transmission between processes
    * :code:`end_reward(bool)`: Whether to enable additional end rewards(additional penalties if end reward is 0; additional rewards if end reward is not 0)
    * :code:`end_reward_list(list)`: Additional end rewards list (valid only when :code:`end_reward` is enabled)
    * :code:`scene(str)`: Determines the current experimental scene (valid only when :code:`auto_start` is enabled)

      * Valid scenes include: :code:`["citystreet", "downtown", "lake", "village", "desert", "farmland", None]`

    * :code:`weather(str)`: Determines the weather of the current experimental scene (valid only when :code:`auto_start` is enabled)

      * Valid weathers include: :code:`["day", "night", "foggy", "snow", None]`

    * :code:`auto_start(bool)`: Whether to automatically start the simulator
    * :code:`delay(int)`: Configure how long the system waits for the map to load, only works if :code:`auto_start(bool)` is enabled.
    * :code:`Control_Frequence(int)`: Specifies the system control frequency
    * :code:`reward_type(str)`: Specifies the type of reward (can choose different baseline algorithms for reward)
    * :code:`verbose(bool)`: Configure the environment to output log files or not

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            2. <code>step</code>: Used for the environment's simulation
      </div>
      </br>

    **Input Parameters:**

    * :code:`action(numpy.int64)`: Action taken by the agent

    .. raw:: html

        </br>

    **Return Parameters:**

    * :code:`image(numpy.ndarray)`: The image returned for the next time step (already post-processed using :code:`process_state`)
    * :code:`reward(float)`: Reward for the current time step
    * :code:`done(bool)`: Whether the current environment has ended
    * :code:`self.SuppleInfo(list)`: Supplementary information (if :code:`Other_State` or :code:`CloudPoint` or :code:`RewardParams` is enabled, it will be retrieved here)

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            2. <code>reset</code>: Used to restart the environment
      </div>
      </br>

    **Input Parameters:**

    None

    **Return Parameters:**

    * :code:`image(numpy.ndarray)`: Same explanation as above
    * :code:`self.SuppleInfo(list)`: Same explanation as above

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


.. _config:

Part 2 Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    .. raw:: html

      <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
            Since the above environment interface has many parameters, <b>this project provides a configuration file</b> to simplify the configuration process. The content of the configuration file is as follows:
      </div>
      </br>

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/config.json</code>
        </div>
        </br>

    .. code:: json

        {
        "Benchmark": {
            "Need_render": 0,
            "Action_dim": 7,
            "State_size": 84,
            "State_channel": 3,
            "Norm_Type": 0,
            "Forward_Speed": 40,
            "Backward_Speed": -40,
            "Left_Speed": 40,
            "Right_Speed": -40,
            "CW_omega": 2,
            "CCW_omega": -2,
            "Control_Frequence": 125,
            "port_process": 39945,
            "end_reward": false,
            "end_reward_list": [
                -20,
                20
            ],
            "scene": "citystreet",
            "weather": "day",
            "auto_start": true,
            "Other_State": false,
            "CloudPoint": false,
            "RewardParams": true,
            "RewardType": "default",
            "verbose": false,
            "delay": 20
        },
            "LunarLander": {
                "Need_render": 1,
                "Action_dim": 4,
                "State_size": 84,
                "State_channel": 3,
                "Norm_Type": 0
            }
        }

    * Among them, :code:`"Benchmark"`: The corresponding parameters are the configuration parameters for the simulation environment proposed in this project.
    * :code:`"LunarLander"`: The parameter configuration for the Gym environment :code:`LunarLander`, used only for compatibility testing.
    * :code:`"Need_render"`: Select rendering mode (Gym environments require a rendering mode; **the default for this project is 0**).
    * :code:`"Action_dim"`: Dimension of the agent's action space.
    * :code:`"State_size"`: Size of the images output by the environment.
    * :code:`"State_channel"`: Number of channels in the images output by the environment (=3 for RGB images, =1 for grayscale images).
    * :code:`"Norm_Type"`: Normalization method for the images (default normalization to :code:`[0,1]`).
    * :code:`"Forward_Speed"`: Speed corresponding to the agent's forward action ( :math:`m/s`).
    * :code:`"Backward_Speed"`: Speed corresponding to the agent's backward action ( :math:`m/s`).
    * :code:`"Left_Speed"`: Speed corresponding to the agent's left movement action ( :math:`m/s`).
    * :code:`"Right_Speed"`: Speed corresponding to the agent's right movement action ( :math:`m/s`).
    * :code:`"CW_omega"`: Speed corresponding to the agent's clockwise action ( :math:`rad/s`).
    * :code:`"CCW_omega"`: Speed corresponding to the agent's counterclockwise action ( :math:`rad/s`).
    * :code:`"Control_Frequence"`: Frequency at which the agent operates (the simulator runs at 500 Hz, while the algorithm side generally runs at 125 Hz).
    * :code:`"port_process"`: Port specified for data transmission between processes.
    * :code:`"end_reward"`: Whether to enable additional end rewards.
    * :code:`"end_reward_list"`: List of additional end rewards (valid only when :code:`end_reward` is enabled).
    * :code:`"scene"`: Determines the current experimental scene (valid only when :code:`auto_start` is enabled).
    * :code:`"weather"`: Determines the weather of the current experimental scene (valid only when :code:`auto_start` is enabled).
    * :code:`"auto_start"`: Whether to automatically start the simulator.
    * :code:`"Other_State"`: Whether to enable additional state options on the simulator side.
    * :code:`"CloudPoint"`: Whether to enable the point cloud option on the simulator side.
    * :code:`"RewardParams"`: Whether to enable additional reward parameters options on the simulator side.
    * :code:`"RewardType"`: Specifies the type of reward (can choose different baseline algorithms for reward).

      * Includes :code:`"default", "E2E", "D-VAT"`, corresponding to :ref:`Built-in Reward`, [1]_, [2]_ reward setting

    * :code:`"verbose"(bool)`: Configures whether the environment outputs log files.
    * :code:`"delay"(int)`: Configures the duration the system waits for the map to load.

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

.. _makeenv:

Part 3 Constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

  <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
        Based on the above configuration file, <b>this project directly provides a constructor to obtain an initialized environment</b>. The usage of this function is as follows:
  </div>
  </br>

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/environment.py</code> in <code>general_env()</code>
    </div>
    </br>

.. code:: python

    # Generate a single-process environment (env_conf is the path to config.json)
    env, _ = general_env(env_id="Benchmark", env_conf=env_conf, arg_worker=1, process_idx=0)

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        <code>general_env</code>: Generates an initialized environment based on the config.json file.
  </div>
  </br>

**Input Parameters:**

* :code:`env_id(str)`: The name of the current environment (:code:`"Benchmark"` or :code:`"LunarLander"`).
* :code:`env_conf(str)`: The path to the configuration file :code:`config.json`.
* :code:`arg_worker(int)`: Total number of processes for the environment.
* :code:`process_idx(int)`: The process index of the current environment.

**Return Parameters:**

* :code:`env`: Environment class.
* :code:`process_func`: Environment post-processing function (for :code:`"Benchmark"`, there are no post-processing operations).

.. raw:: html

    </br>

.. _Gymnasium_Gym:


2 Gym Environment class
-------------------------------------------------

Considering that users often build reinforcement learning algorithms based on `Gym <https://github.com/openai/gym>`_ and `Gymnasium <https://github.com/openai/gym>`_ environment interfaces, or utilize libraries such as `stable-baselines3 <https://github.com/DLR-RM/stable-baselines3>`_ for algorithm validation, this project encapsulates the aforementioned base environment class to provide fully compatible environment classes for `Gym <https://github.com/openai/gym>`_ and `Gymnasium <https://github.com/openai/gym>`_.

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
      See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/envs_parallel.py</code>
    </div>
    </br>


Part1 UAV_VAT (Adapting to Gym Library)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/gym_envs.py</code> in the <code>UAV_VAT(gym.Env)</code> class
        </div>
        </br>

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        1. <code>__init__</code>: Initializes the gym environment (including initialization of <code>action_space</code> and <code>observation_space</code>).
  </div>
  </br>

**Input Parameters:**

* :code:`arg_worker(int)`: Number of processes.
* :code:`conf_path(list)`: Path to the environment configuration file.
* :code:`env_conf_path(list)`: Path to the simulator configuration file.
* :code:`process_idx(list)`: Current process index.

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        2. <code>reset</code>: Resets the environment, returning the initial state.
  </div>
  </br>

**Return Parameters:**

* :code:`state(np.ndarray)`: Returns the state (image).

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        3. <code>step</code>: Environment interaction, inputs action, retrieves state information.
  </div>
  </br>

**Input Parameters:**

* :code:`action(torch.tensor)`: Action.

**Return Parameters:**

* :code:`state(np.ndarray)`: Returns the state (image).
* :code:`reward(float)`: Reward.
* :code:`done(int)`: Whether the environment has ended.
* :code:`info(dict)`: Information, including :code:`info["TimeLimit.truncated"]` which indicates whether the reset was due to step ending.

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


Part 2 UAV_VAT_Gymnasium (Adapting to Gymnasium Library)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Gymnasium environment is largely compatible with the Gym environment, and the following describes the differences from the Gym environment.

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;"> See the specific code in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/gym_envs.py</code> in the <code>UAV_VAT_Gymnasium(gymnasium.Env)</code> class. </div> </br>

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;"> 1. <code>reset</code>: Resets the environment, returning the initial state. </div> </br>

Input Parameters:

    :code:`seed(int)`: Random seed.

Return Parameters:

    :code:`reset_info(dict)`: Reset environment information (default is empty).

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;"> 2. <code>step</code>: Environment interaction, inputs action, retrieves state information. </div> </br>

Return Parameters:

    :code:`truncated(bool)`: Whether the reset was due to step ending (equivalent to :code:`info["TimeLimit.truncated"]` in Gym environment).

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

.. _SubprovecEnv:

Part3 Parallel Environment Encapsulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

  <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
  <b>Stacked environment for parallel computation</b>, enabling multiple environments to interact with multiple agents.
  </div>
  </br>

.. raw:: html

  <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
      For specific code, see the <code>ASYNC_SubprocVecEnv</code> class in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/async_vecenv.py</code>.
      Also, see the <code>SubprocVecEnv_TS</code> class in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/async_vecenv_ts.py</code>.
  </div>
  </br>

**Existing Reinforcement Learning Library Parallel Class Features and Modifications in This Project**

  * Existing reinforcement learning libraries directly compatible with gym environments, such as the :code:`stable-baselines3` and :code:`tianshou` libraries, provide the parallel environment class :code:`SubprocVecEnv` , allowing users to directly encapsulate gym environments into parallel environments.
  
  * The above-mentioned :code:`SubprocVecEnv` environment class checks whether to execute ``reset`` immediately after executing ``step``, which may cause the ``step`` and :code:`reset` to be executed in the same cycle.(Not strictly aligned with :code:`step` and :code:`reset` as required by the project environment.)

  * Modification in this project: Strictly align :code:`step` with :code:`reset` to keep individual environment operations synchronized.

  * The :code:`SubprocVecEnv` class from the ``stable-baselines3`` library is modified to the ``Async_SubprocVecEnv`` class, and the ``SubprocVecEnv`` and ``Collector`` classes from the ``tianshou`` library are modified to ``SubprocVecEnv_TS`` and ``TS_Collector`` classes, respectively.

  * The differences between the original and modified implementations are shown in the figure below.

.. raw:: html

  <img src="../_static/image/subprovecenv.png" alt="Comparison of Async_SubprocVecEnv before and after modifications">
  <center>comparison diagram of SubprocVecEnv before and after modification</center></br>


.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


Part 4 Interface Invocation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

  <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
      For specific code, see the <code>make_env()</code> function in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/envs_parallel.py</code>.
  </div>
  </br>

.. raw:: html

  <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
        <code>make_env</code>: Initializes multiple gym environments.
  </div>
  </br>

**Input Parameters:**

* :code:`n_envs(int)`: Number of environments.
* :code:`rank(int)`: Current environment index.
* :code:`gym(bool)`: If :code:`True`, generates environments from the Gym library; if :code:`False`, generates environments from the Gymnasium library.
* :code:`monitor(bool)`: Whether to wrap in the :code:`stable_baselines3.common.monitor.Monitor` class.

**Test Code:**

.. raw:: html

  <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
      For specific code, see the <code>gym_test()</code> function and <code>stableparallel_test()</code> function in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/envs_parallel.py</code>.
  </div>
  </br>

If you wish to quickly test whether the implementation of the above environment class is correct, you can use the following code:

  1. Single process (using only gym environment)

  .. code:: python

    from gym.envs.registration import register

    register(
        id='UAVVAT-v0',
        entry_point='gym_envs:UAV_VAT',
    )

    gym_test()

  2. Use stable-baselines3 for algorithm testing

    .. code:: python

      stableparallel_test(n_envs=16, gym=False)

    .. raw:: html

      <div style="border-left: 4px solid #FFC1C1; padding-left: 10px; margin-left: 0;">
        <b>Note:</b> When using the stable-baselines3 library for parallel training, invoke the above <b>Async_SubprocVecEnv</b> class.
      </div>

  3. Use tianshou for algorithm testing

    .. code:: python

      test_tianshou_env(args)

    .. raw:: html

      <div style="border-left: 4px solid #FFC1C1; padding-left: 10px; margin-left: 0;">
        <b>Note:</b> When using the tianshou library for parallel training, you need to invoke the above <b>SubprocVecEnv_TS</b> class.
      </div></br>

.. _Parallel:

3 Parallel Environment Classes
-------------------------------------------------
.. raw:: html

  <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
    <blockquote>
    <p>The design goal of the base environment class (BenchEnv_Multi) is <strong>multi-process asynchronous computation</strong> (e.g., A3C algorithm), calling the environment class to obtain data within individual processes.</p>
    <p>To better utilize the GPU for parallel acceleration, synchronize the data of the above classes and execute the same commands in parallel, allowing the algorithm to <strong>operate in a single process on a synchronized parallel data flow</strong>, leading to this class (Envs).</p>
    <p>This environment is primarily tailored to <strong>user-defined algorithm design needs</strong> (in scenarios where stable-baselines3 and other Gym-based environments are not used for algorithm implementation).</p>
    </blockquote>
  </div>
  </br>
  </br>


.. raw:: html

  <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
      For specific code, see the <code>Envs</code> class in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/envs_parallel.py</code>.
  </div>
  </br>

Part 1 Envs()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            For specific code, see the <code>Envs</code> class in <code>Alg_Base/rl_a3c_pytorch_benchmark/envs/envs_parallel.py</code>.
        </div>
        </br>

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        1. <code>__init__</code>: Initializes the Envs parallel environment (including the initialization of <code>action_space</code> and <code>observation_space</code>).
  </div>
  </br>

**Input Parameters:**
  * :code:`num_envs(int)`: Represents the concurrency level n.

  * :code:`env_list(list(env))`: Initialize the list returned by the :code:`GE(n)` function by storing a number of pre-constructed environment classes in the list

  * :code:`logs_show(bool)` ：Whether to collect reward data in one of the environments to draw a training curve


.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        2. <code>reset</code> ：reset environment, and return to the init environment
  </div>
  </br>

**Return Parameters：**

* :code:`states` ：Returns a collection of states (images) for each environment

.. raw:: html

  <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        3. <code>step</code> ：Environment interaction, input action, get status information
  </div>
  </br>

**Input Parameters：**

* :code:`actions` ：Each Agent action

**Return Parameters：**

* :code:`states` ：Returns a collection of states (images) for each environment
* :code:`rewards` ：The reward stack for each Agent
* :code:`done` ：Whether each environment is in the end state

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


Part2 Data format changes before and after encapsulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Comparison of data formats before and after encapsulation：**

* Pre-package(BenchEnv_Multi):

  Data sampling： :code:`state:ndarray,reward:float,done:float= env.step(action:int)`

  Environment reset： :code:`state:ndarray = env.reset()`

* After packaging(Envs), set the parallel number n：

  Data sampling： :code:`states:ndarray(n,),rewards:ndarray(n),done:ndarray(n)= env.step(action:ndarray(n))`

  Environment reset： :code:`states:ndarray(n,) = envs.reset()`


.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

4 Performance Evaluation Metrics
------------------------------------------------------------------------------------------

1. Cumulative Reward CR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The cumulative reward uses continuous rewards, and a cumulative calculation is performed to evaluate the performance of the intelligent body in keeping the target at the center of the image, as shown in the following formula:

.. raw:: html

    <math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mi>C</mi><mi>R</mi><mo>=</mo><munderover><mo data-mjx-texclass="OP">∑</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mrow><msub><mi>E</mi><mi>l</mi></msub></mrow></munderover><msub><mi>r</mi><mrow><mi>c</mi><mi>t</mi></mrow></msub></math>
    </br>

In the above formula, :math:`r_{ct}` represents the continuous reward value at step :math:`t`, :math:`E_{ml}` represents the maximum trajectory length, and :math:`E_t` represents the length of this trajectory.
For a graphical representation of continuous reward calculation, see :ref:`Continuous Reward Diagram for Tracking Object`.

2. Tracking Success Rate TSR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  This metric uses discrete rewards to evaluate the proportion of successful tracking, calculated using the following formula:

.. raw:: html

   <math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mi>T</mi><mi>S</mi><mi>R</mi><mo>=</mo><mfrac><mn>1</mn><msub><mi>E</mi><mrow><mi>m</mi><mi>l</mi></mrow></msub></mfrac><munderover><mo data-mjx-texclass="OP">∑</mo><mrow><mi>t</mi><mo>=</mo><mn>1</mn></mrow><mrow><msub><mi>E</mi><mi>t</mi></msub></mrow></munderover><msub><mi>r</mi><mrow><mi>d</mi><mi>t</mi></mrow></msub><mo>×</mo><mn>100</mn><mi mathvariant="normal">%</mi></math>
   </br>

In the above formula, :math:`r_{dt}` represents the discrete reward value at step :math:`t`, :math:`E_{ml}` is the maximum step length across batches, and :math:`E_l` represents the length of the current batch. Detail parameters see: :ref:`Built-in reward parameter configuration`
For a graphical representation of discrete reward calculation, see :ref:`Discrete Reward Diagram for Tracking Object`.

.. raw:: html

  </br>
  <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
  </br>
  </br>

Reference:

.. [1] Luo, Wenhan, et al. "End-to-end active object tracking and its real-world deployment via reinforcement learning." IEEE transactions on pattern analysis and machine intelligence 42.6 (2019): 1317-1332.
.. [2] Dionigi, Alberto, et al. "D-VAT: End-to-End Visual Active Tracking for Micro Aerial Vehicles." IEEE Robotics and Automation Letters (2024).