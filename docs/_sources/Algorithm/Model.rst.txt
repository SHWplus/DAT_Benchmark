Model Construction
==================

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
                window.location.href = '../../zh/Algorithm/Model.html';
            } else if (lang === 'en') {
                window.location.href = '../../en/Algorithm/Model.html';
            }
        }
    </script> 

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


.. raw:: html

    <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 2px solid #CD6839;">
        This project provides algorithm implementations of three baseline methods, namely <code>A3CLSTM-E2E</code> [1], <code>D-VAT</code> [2], and <code>R-VAT(Ours)</code>.
    </div>
    </br>

Among these baseline methods, [1]_ [2]_ and :code:`R-VAT(Ours)` respectively call the three environments implemented in this project( :doc:`Environment` ), providing templates for different algorithm implementation needs.

*  The :code:`A3CLSTM-E2E` algorithm calls the underlying environment class ( :ref:`BenchEnv_Multi` )
*  The :code:`D-VAT` algorithm calls the Gym environment class ( :ref:`Gymnasium_Gym` )
*  The :code:`R-VAT` algorithm calls the parallel environment class ( :ref:`Parallel` )

.. figure:: ../_static/image/classes.png
    :alt: 3种环境类关系图                                 
    :width: 600px                                              
    :align: center


.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

Baseline1 A3CLSTM-E2E
---------------------------------

This project refers to the paper :code:`AD-VAT+` [3]_ for reproducing the :code:`A3CLSTM-E2E` method based on the repository `rl_a3c_pytorch <https://github.com/dgriff777/rl_a3c_pytorch>`_.

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        The specific code can be found in the <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E</code> folder
    </div>
    </br>

Quick-Start
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Testing with Cumulative Reward (CR)
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode CR
    # Testing with Tracking Success Rate (TSR)
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode TSR
    # New training mode
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125 --New_Train
    # Resumed training mode
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125

Program entry point
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`main.py` is the entry point of the entire program, primarily providing two operating modes: :code:`train` and :code:`test`.
        
        * In :code:`train` mode, a testing process is also provided (e.g., if the program runs with 24 processes, the last process with ID 23 will be used for testing). This process is mainly used for :code:`tensorboard` visualization during the training process.
        * The :code:`test` mode is mainly used to test the model weights after training is completed. This mode runs in a single process and tests the weights of individual models.
        * The configuration variable for the above modes is the :code:`MODE` variable.

    In addition, the :code:`main.py` file also accepts user parameter configurations, with the meanings and default values of the parameters as follows:
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. Runtime parameters:</b> Configure system mode, runtime frequency, device settings, etc.
      </div>
      </br>

    * :code:`--Mode(int)=1` : Configure whether the running mode is training mode (:code:`--Mode=1` for training mode, :code:`--Mode=0` for testing mode)
    * :code:`--workers(int)=35` : The number of parallel training processes in the environment (should be determined based on the actual memory/GPU capacity of the computer)
    * :code:`--gpu-ids(list)=[-1]` : Used to set the GPU IDs, default is -1, which means no GPU will be used
    * :code:`--Freq(int)=125` : The running frequency of the algorithm side (the environment side runs at 500Hz and is unchangeable), so the default :code:`--Freq(int)=125` means the environment side transmits data back every 4 steps
    * :code:`--delay(int)=20` : Waiting time for Webots map to load (training can only start normally after the Webots map has been fully loaded)
    * :code:`--New_Train(bool)=False` : Whether to start a new training session, default is :code:`--New_Train=False`, which will load the pre-trained weights from :code:`A3CLSTM_E2E/trained_models/Benchmark.dat` (if available) for training, and the tensorboard curves will continue from the last training session
    * :code:`--Port(int)=-1` : The communication port between the environment side and the algorithm side, default :code:`--Port=-1` will randomly use an available port, and manual **modification is not recommended**

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. Environment parameters:</b> Configure the selected environment
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : Configure the training/testing environment scene type, choose from :code:`[citystreet-day.wbt,downtown-day.wbt,lake-day.wbt,village-day.wbt,desert-day.wbt,farmland-day.wbt,citystreet-night.wbt,downtown-night.wbt,lake-night.wbt,village-night.wbt,desert-night.wbt,farmland-night.wbt,citystreet-foggy.wbt,downtown-foggy.wbt,lake-foggy.wbt,village-foggy.wbt,desert-foggy.wbt,farmland-foggy.wbt,citystreet-snow.wbt,downtown-snow.wbt,lake-snow.wbt,village-snow.wbt,desert-snow.wbt,farmland-snow.wbt]` 
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. Model parameters:</b> Configure parameters related to model weight loading and saving
      </div>
      </br>
    
    * :code:`--load(bool)=True` : Whether to load an existing model for further training (only when :code:`--load=True` and the model weights :code:`A3CLSTM_E2E/trained_models/Benchmark.dat` exist will the model be loaded)
    * :code:`--save-max(bool)=False` : Whether to save the model weights when the testing process reaches the highest reward, default is :code:`False`, meaning only the model weights at the last moment will be saved
    * :code:`--model_type(str)="E2E"` : Specify the type of model currently being used, if the user implements their own model, they can add the configuration here
    * :code:`--save-model-dir(str)="./models/A3CLSTM_E2E/trained_models/"` : The path for saving the model
    * :code:`--Test_Param(str)="CityStreet-d"` : Specifies which weights to load for testing(only enabled when :code:`--Mode(int)=0`), default is :code:`--Test_Param="CityStreet-d"`, which will load the weights :code:`A3CLSTM_E2E/trained_models/CityStreet-d.dat` for testing

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. Visualization parameters:</b> Configure parameters related to visualization files
      </div>
      </br>
    
    * :code:`--tensorboard-logger(bool)=True` : Whether to enable :code:`tensorboard` for model visualization
    * :code:`--log-dir(str)="./models/A3CLSTM_E2E/logs/"` : If :code:`tensorboard` is enabled, the location to store the log files

log files
~~~~~~~~~~~~~~~~~~~~~~~~~

    This project provides two types of log recording methods. The first is to directly output log files (configured through :code:`config.json` in :code:`["Benchmark"]["verbose"]`), and the second is to use TensorBoard to record performance changes during the training process.

    **Mode 1: Directly output log files**

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            Log files can be found in the folder <code>Alg_Base/DAT_Benchmark/logs</code>
        </div>
        </br>

    * This mode is mainly used for program debugging and data transmission verification, essentially replacing the terminal :code:`print` function.
    *  :code:`Agent${n}.log` is mainly used to save the data transmitted from the environment. For example, if you want to observe the custom reward parameters :code:`RewardParams` obtained from the environment, you can view them in this file.

    **Mode 2: Directly output tensorboard-logger files**

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            TensorBoard-logger files can be found in the folder <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E/runs/Benchmark_training</code>
        </div>
        </br>

    * :code:`TensorBoard` is a commonly used visualization platform during the training process of neural networks. Therefore, this project also provides corresponding support.
    * During multi-process training, this project reserves one process for testing. For example, if the user selects 24 parallel agents, then during the actual training, there will be 23 training processes and 1 testing process. The testing process synchronizes the weights of the shared_model at the beginning of each episode and conducts tests.
    * The data recorded in the :code:`tensorboard-logger` file is from the testing process, mainly the :code:`value` during training, which is used to evaluate the training status of the agents.
    * Additionally, if the program is interrupted due to external reasons, this project provides an uninterrupted :code:`tensorboard-logger` function. It uses :code:`num_test.txt` to store the current data entry count and continues recording when a new training session starts.
    * **Note:** If the user wishes to re-record the training curve, they need to add :code:`-- New_Train` to the command that starts the training.
    * After completing all configurations, simply run the following code to view the :code:`TensorBoard` visualization records on :code:`localhost:xxxx`.
    
    .. code:: bash

        cd Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E/runs
        tensorboard --logdir Benchmark_training

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

Baseline2 D-VAT
---------------------------------

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        The specific code can be found in the <code>Alg_Base/DAT_Benchmark/models/D_VAT</code> folder.
    </div>
    </br>


Quick-Start
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Test using Cumulative Reward (CR)
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode AR
    # Test using Tracking Success Rate (TSR)
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # New training mode
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # Resume training mode after interruption
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1

Program Entry
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`DVAT_main.py` is the entry point of the entire program, providing both training and testing modes (specific configurations can be found in the parameters section below).

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. Run Parameters:</b> Configure system mode, run frequency, device, and other parameters.
      </div>
      </br>

    * :code:`--workers(int)=35` : The number of parallel training environments (this should be decided based on the actual memory/GPU of the computer).
    * :code:`--train_mode(int)=1` : Configure whether the operation mode is training mode (:code:`--train_mode=1` is training mode, :code:`--train_mode=0` is testing mode).
    * :code:`--port(int)=-1` : Communication port between the environment and algorithm end. By default, :code:`--port=-1` uses a randomly available port. Manual modification is not recommended.
    * :code:`--New_Train(bool)=False` : Whether to start a new training session. The default is :code:`--New_Train=False`, which will load :code:`params.pth` pretrained weights (if available) for training, and the tensorboard curve will also load from the last training session.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. Environment Parameters:</b> Configure the selected environment.
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : Configure the training/testing environment scene type, selected from :code:`./Webots_Simulation/traffic_project/worlds/*.wbt`.
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. Model Parameters:</b> Configure parameters related to model weight import and saving.
      </div>
      </br>

    * :code:`--savepath(str)="params.pth"` : Path where the model will be saved.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. Visualization Parameters:</b> Configure parameters related to visualization files.
      </div>
      </br>

    * :code:`--tensorboard_port(int)=1` : Whether to use tensorboard-logger. If :code:`--tensorboard_port(int)!=-1`, a random available port will be assigned; otherwise, it will not be enabled (not enabled in testing mode).


Code Encapsulation and Modification Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    D-VAT adopts an Actor-Critic asymmetric framework. The schematic diagrams of the Actor-Critic symmetric and asymmetric architectures are as follows:

    .. figure:: ../_static/image/sym_asym.png
        :alt: Asymmetric_and_Symmetrical_Structure
        :width: 700px
        :align: center

        Schematic diagrams of the Actor-Critic symmetric and asymmetric architectures


    **The D-VAT code mainly implements the following:**

    1. Custom Environment Class

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            The environment class is modeled after the <a href="./Environment.html#gym">Gym environment class</a> to independently implement the <code>DVAT_ENV</code> environment class, with the specific code seen in <code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_envs.py</code><br>
            To support the Actor-Critic asymmetric architecture, the state space of the <code>DVAT_ENV</code> environment class includes two parts: <code>actor_obs</code> and <code>critic_obs</code>:
        </div>
        </br>

    .. code:: python

        self.observation_space = gymnasium.spaces.Dict({
            "actor_obs": gymnasium.spaces.Box(low=0, high=1.0, shape=(obs_buffer_len,)+image_shape, dtype=np.float32),
            "critic_obs": gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(9,), dtype=np.float32),
        })

    In the original gymnasium environment, the actor and critic share the same state space:

    .. code:: python

        if obs_buffer_len == 0:
            self.observation_space = spaces.Box(low=0, high=1.0, shape=(env_conf["State_channel"], env_conf["State_size"], env_conf["State_size"]), dtype=np.float32)
        else:
            self.observation_space = spaces.Box(low=0, high=1.0, shape=(obs_buffer_len, env_conf["State_channel"], env_conf["State_size"], env_conf["State_size"]), dtype=np.float32)



    2. Custom Implemented Policy

    To support the Actor-Critic asymmetric architecture, the :code:`DVAT_SACDPolicy` is implemented by inheriting from **Tianshou**'s :code:`DiscreteSACPolicy`.

    3. Custom Implemented Parallel Class and Collector
    
    Custom parallel environment classes and collectors are implemented by referring to `Async_SubprocVecEnv & SubprocVecEnv_TS <Environment.html#part3-async-subprocvecenv-subprocvecenv-ts>`_.


log file
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            See the tensorboard-logger file in the folder <code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_logs</code>
        </div>
        </br>

    * During the model training process, as long as the parameter :code:`--tensorboard_port(int)!=-1` is set, the tensorboard-logger will automatically start when the program is launched.
    * However, if you want to manually start tensorboard, you can also use the following command:

    .. code:: bash

        cd Alg_Base/DAT_Benchmark/models/D_VAT/
        tensorboard --logdir DVAT_logs


.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


Baseline3 R-VAT
---------------------------------

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        For specific code, see <code>Alg_Base/DAT_Benchmark/models/R_VAT</code> folder
    </div>
    </br>

Quick-Start
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Test with Cumulative Reward (CR)
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode AR
    # Test with Tracking Success Rate (TSR)
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # New training mode
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # Resume training mode
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1

Program Entry
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`RVAT.py` is the entry point for the entire program, providing both training and testing modes (for specific configurations, refer to the parameter settings below).

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. Runtime Parameters:</b> Configure system mode, execution frequency, device, and other parameters
      </div>
      </br>

    * :code:`--workers(int)=35` : The number of parallel environments for training (should be determined by the actual memory/VRAM of the computer).
    * :code:`--train_mode(int)=1` : Configure whether the mode is training mode ( :code:`--train_mode=1` is training mode, :code:`--train_mode=0` is testing mode).
    * :code:`--port(int)=-1` : Communication port between environment and algorithm, default :code:`--port=-1` will randomly use an available port, manual modification is not recommended.
    * :code:`--New_Train(bool)=False` : Whether to start a completely new training, default is :code:`--New_Train=False`, which loads :code:`params.pth` pre-trained weights (if available) for training, and tensorboard curves will be loaded from the last training session.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. Environment Parameters:</b> Configure the selected environment
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : Configure the training/testing environment scene type, selected from :code:`./Webots_Simulation/traffic_project/worlds/*.wbt`.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. Model Parameters:</b> Configure model weight import and save related parameters
      </div>
      </br>

    * :code:`--savepath(str)="params.pth"` : Path where the model will be saved.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. Visualization Parameters:</b> Configure parameters related to visualization files
      </div>
      </br>

    * :code:`--tensorboard_port(int)=1` : Whether to use tensorboard-logger, :code:`--tensorboard_port(int)!=-1` will randomly assign an available port, otherwise it will not be enabled (not enabled in testing mode).


Curriculum Learning
~~~~~~~~~~~~~~~~~~~~~~~~~

    * Our method adds curriculum learning based on R-VAT, and in the first and second stages of curriculum learning, the intelligent experience tracks monochrome and colored cars respectively under simple settings (unobstructed situation, car only travels straight)
    * For convenience, we extracted the simple settings as maps, i.e. :code:`./Webots_Simulation/traffic_project/worlds/simpleway-*.wbt` maps.
    * Therefore, the third stage is trained on the corresponding :code:`simpleway-*.wbt`.
    * After completing task understanding, the third stage of training can be conducted on visually challenging maps to learn complex visual features.
    * For example, for the map :code:`citystreet-day.wbt`, the commands for the third stages are as follows:

    .. code:: bash

        cd Alg_Base/DAT_Benchmark/
        # Stage2: Task Understanding
        python ./models/R_VAT/RVAT.py -w 35 -m simpleway-grass.wbt --train_mode 1 --New_Train
        # Stage3: Visual Generalization
        python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1
        # Testing Mode
        # Test with Cumulative Reward (CR)
        python ./models/R_VAT/RVAT.py -w 1 -m citystreet-night.wbt --train_mode 0 --Test_Mode AR
        # Test with Tracking Success Rate (TSR)
        python ./models/R_VAT/RVAT.py -w 1 -m citystreet-night.wbt --train_mode 0 --Test_Mode TSR

.. _table-cf:

      * The comparison table of the two-stage maps is as follows:

        +------------------+-------------------------+
        | Origin Map       | Simple Map              |
        +==================+=========================+
        |citystreet-day    |simpleway-grass_day      |
        +------------------+-------------------------+
        |citystreet-night  |simpleway-grass_night    |
        +------------------+-------------------------+
        |citystreet-foggy  |simpleway-grass_foggy    |
        +------------------+-------------------------+
        |citystreet-snow   |simpleway-city_snow      |
        +------------------+-------------------------+
        |desert-day        |simpleway-desert_day     |
        +------------------+-------------------------+
        |desert-night      |simpleway-desert_night   |
        +------------------+-------------------------+
        |desert-foggy      |simpleway-desert_foggy   |
        +------------------+-------------------------+
        |desert-snow       |simpleway-desert_snow    |
        +------------------+-------------------------+
        |downtown-day      |simpleway-clinker_day    |
        +------------------+-------------------------+
        |downtown-night    |simpleway-clinker_night  |
        +------------------+-------------------------+
        |downtown-foggy    |simpleway-clinker_foggy  |
        +------------------+-------------------------+
        |downtown-snow     |simpleway-city_snow      |
        +------------------+-------------------------+
        |farmland-day      |simpleway-farm_day       |
        +------------------+-------------------------+
        |farmland-night    |simpleway-farm_night     |
        +------------------+-------------------------+
        |farmland-foggy    |simpleway-farm_foggy     |
        +------------------+-------------------------+
        |farmland-snow     |simpleway-farm_snow      |
        +------------------+-------------------------+
        |lake-day          |simpleway-lake_day       |
        +------------------+-------------------------+
        |lake-night        |simpleway-lake_night     |
        +------------------+-------------------------+
        |lake-foggy        |simpleway-lake_foggy     |
        +------------------+-------------------------+
        |lake-snow         |simpleway-lake_snow      |
        +------------------+-------------------------+
        |village-day       |simpleway-village_day    |
        +------------------+-------------------------+
        |village-night     |simpleway-village_night  |
        +------------------+-------------------------+
        |village-foggy     |simpleway-village_foggy  |
        +------------------+-------------------------+
        |village-snow      |simpleway-village_snow   |
        +------------------+-------------------------+

log file
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            The tensorboard-logger file can be found in the folder <code>Alg_Base/DAT_Benchmark/models/${model_name}_logs</code>
        </div>
        </br>

    * During the model training process, as long as the parameter :code:`--tensorboard_port(int)!=-1` is set, the tensorboard-logger will automatically start when the program is launched.
    * However, if you wish to start tensorboard manually, you can use the following command:

    .. code:: bash

        cd Alg_Base/DAT_Benchmark/
        tensorboard --logdir models/${model_name}_logs

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


Reference:

.. [1] Luo, Wenhan, et al. "End-to-end active object tracking and its real-world deployment via reinforcement learning." IEEE transactions on pattern analysis and machine intelligence 42.6 (2019): 1317-1332.
.. [2] Dionigi, Alberto, et al. "D-VAT: End-to-End Visual Active Tracking for Micro Aerial Vehicles." IEEE Robotics and Automation Letters (2024).
.. [3] Zhong, Fangwei, et al. "Ad-vat+: An asymmetric dueling mechanism for learning and understanding visual active tracking." IEEE transactions on pattern analysis and machine intelligence 43.5 (2019): 1467-1482.



