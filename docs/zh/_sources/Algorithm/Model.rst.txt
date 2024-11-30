模型搭建
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
                window.location.href = 'Model.html';
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
        本工程提供了3种baseline方法的算法实现，分别是 <code>A3CLSTM-E2E</code> [1] , <code>D-VAT</code> [2] , 以及 <code>R-VAT(Ours)</code>
    </div>
    </br>


其中，上述baseline方法中 [1]_ [2]_ 和 :code:`R-VAT` 分别调用了本工程实现的3种环境( :doc:`Environment` )，为不同需求的算法实现提供了模板。

*  :code:`A3CLSTM-E2E` 算法调用了底层环境类( :ref:`BenchEnv_Multi` )
*  :code:`D-VAT` 算法调用了Gym环境类( :ref:`Gymnasium_Gym` )
*  :code:`R-VAT` 算法调用了并行环境类( :ref:`Parallel` )

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

本工程对于 :code:`A3CLSTM-E2E` 方法的复现参考了论文 :code:`AD-VAT+` [3]_ 基于代码仓库 `rl_a3c_pytorch <https://github.com/dgriff777/rl_a3c_pytorch>`_ 的复现方式。

.. raw:: html

    <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
        具体代码见 <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E</code>文件夹
    </div>
    </br>

快速运行程序
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # 测试模式
    # 使用 累计奖励 CR 进行测试
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode CR
    # 使用 追踪成功比例 TSR 进行测试
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode TSR
    # 新训练模式
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125 --New_Train
    # 中断重开训练模式
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125

程序入口
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`main.py` 为整个程序的入口，主要提供两种运行模式：:code:`train` 和 :code:`test` 。
        
        * 其中， :code:`train` 模式下同样提供了测试进程(例如程序以24进程运行，那么最后一位进程编号23对应的进程为测试进程)， 该进程主要用于训练过程的 :code:`tensorboard` 可视化
        * 而 :code:`test` 模式主要利用已经完成训练的模型权重进行测试，该模式单进程运行，对单个模型权重进行测试。
        * 上述模式的配置变量为 :code:`MODE` 变量

    此外， :code:`main.py` 文件还接收用户的参数配置，参数的含义与默认值如下：
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. 运行参数：</b>配置系统模式，运行频率，设备等参数
      </div>
      </br>

    * :code:`--Mode(int)=1` : 配置运行模式是否为训练模式( :code:`--Mode=1` 是训练模式，:code:`--Mode=0` 是测试模式)
    * :code:`--workers(int)=35` ：并行环境数量(需要根据实际计算机的内存/显存来决定)
    * :code:`--gpu-ids(list)=[-1]` ：用于设置GPU的编号，默认为-1，即不使用GPU
    * :code:`--Freq(int)=125` ：算法端运行频率(环境端运行频率为500Hz是不可修改的)，因此默认 :code:`--Freq(int)=125` 即环境端运行4步回传一次数据
    * :code:`--delay(int)=20` : 等待Webots地图加载时长(只有等Webots地图加载完成之后才能够正常开始训练)
    * :code:`--New_Train(bool)=False` : 是否开启全新的训练，默认为 :code:`--New_Train=False`，则会加载 :code:`A3CLSTM_E2E/trained_models/Benchmark.dat` 预训练权重(如果存在)进行训练，并且tensorboard的曲线也会从上一次训练曲线后加载
    * :code:`--Port(int)=-1` : 环境端与算法端通信端口，默认 :code:`--Port=-1` 则随机利用一个当前可用的端口， **不建议手动修改**
    * :code:`--verbose(bool)=False` : 是否开启Agent动作行为与环境奖励等记录数据
    * :code:`--Test_Mode(str)=CR` : 选择测试评估方式为 CR 或 TSR
    * :code:`--test_length(int)=10` : 测试episode长度
    * :code:`--observation_buffer_length(int)=3` : 观测状态使用的帧数量


    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. 环境参数：</b>配置选择的环境
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : 配置训练/测试环境场景种类，从 :code:`[citystreet-day.wbt,downtown-day.wbt,lake-day.wbt,village-day.wbt,desert-day.wbt,farmland-day.wbt,citystreet-night.wbt,downtown-night.wbt,lake-night.wbt,village-night.wbt,desert-night.wbt,farmland-night.wbt,citystreet-foggy.wbt,downtown-foggy.wbt,lake-foggy.wbt,village-foggy.wbt,desert-foggy.wbt,farmland-foggy.wbt,citystreet-snow.wbt,downtown-snow.wbt,lake-snow.wbt,village-snow.wbt,desert-snow.wbt,farmland-snow.wbt]` 中选择
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. 模型参数：</b>配置模型权重导入和保存相关参数
      </div>
      </br>
    
    * :code:`--load(bool)=True` ：是否导入现有模型进行进一步的训练(只有当 :code:`--load=True` 以及而且模型权重 :code:`A3CLSTM_E2E/trained_models/Benchmark.dat` 存在的时候才会导入)
    * :code:`--save-max(bool)=False` ： 是否保存测试进程reward最大时刻的模型权重，默认为 :code:`False` 即仅保存最后一个时刻的模型权重
    * :code:`--model_type(str)="E2E"` ： 指定当前使用的模型种类，如果用户自主实现了模型可以在此处增加配置。
    * :code:`--save-model-dir(str)="./models/A3CLSTM_E2E/trained_models/"` ：模型保存的路径
    * :code:`--Test_Param(str)="Benchmark"` : 导入什么权重进行测试(须 :code:`--Mode(int)=0` )。默认为 :code:`--Test_Param="Benchmark"`，会导入权重 :code:`A3CLSTM_E2E/trained_models/Benchmark.dat` 进行测试

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. 可视化参数：</b>配置可视化文件相关参数
      </div>
      </br>
    
    * :code:`--tensorboard-logger(bool)=True` ：是否使能 :code:`tensorboard` 进行模型的可视化
    * :code:`--log-dir(str)="./models/A3CLSTM_E2E/logs/"` ：如果开启了 :code:`tensorboard` ，log文件存储的位置

log文件
~~~~~~~~~~~~~~~~~~~~~~~~~

    本工程提供了两种log记录方式，第一种是直接输出log文件(通过 :code:`config.json` 中的 :code:`["Benchmark"]["verbose"]` 进行配置)，另外一种是利用tensorboard记录训练过程的性能变化。

    **模式1：直接输出log文件**

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            log文件见文件夹 <code>Alg_Base/DAT_Benchmark/logs</code>
        </div>
        </br>

    * 仅当 :code:`verbose` 开启是，方才输出log文件
    * 本模式主要用于程序的调试和数据传输验证，相当于是终端 :code:`print` 函数的替代
    *  :code:`Agent${n}.log` 主要用于保存环境端传输的数据，例如希望观测环境端获取的自定义奖励参数 :code:`RewardParams` ，则可以在该文件观测

    **模式2：直接输出tensorboard-logger文件**

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            tensorboard-logger文件见文件夹 <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E/runs/Benchmark_training</code>
        </div>
        </br>

    * :code:`tensorboard` 是神经网络训练过程中的常用可视化平台，因此，本工程也提供了相应的支持
    * 本工程在进行多进程训练的时候会预留一个进程进行测试，例如：用户选择并行智能体数量为35,则实际训练的过程中会有23个训练进程以及1个测试进程，测试进程在每条Episode开始的时候同步shared_model的权值，并进行测试。
    * 而 :code:`tensorboard-logger` 文件中记录的就是测试进程的数据，主要是训练过程中的 :code:`value` ，用于评估智能体训练的情况
    * 此外，如果程序因为外部原因中断，本工程提供了 :code:`tensorboard-logger` 不中断功能，利用 :code:`num_test.txt` 存储当前数据条目数，并在新训练开始时继续进行记录。
    * **注意：** 如果用户希望重新记录训练曲线，则需要在启动训练的命令中添加 :code:`--New_Train`。
    * 完成所有配置之后，直接运行如下代码，即可在 :code:`localhost:xxxx` 查看 :code:`tensorboard` 可视化记录
    
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
        具体代码见 <code>Alg_Base/DAT_Benchmark/models/D_VAT</code>文件夹
    </div>
    </br>


快速运行程序
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # 测试模式
    # 使用 累计奖励 CR 进行测试
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode CR
    # 使用 追踪成功比例 TSR 进行测试
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # 新训练模式
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # 中断重开训练模式
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1

程序入口
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`DVAT_main.py` 为整个程序的入口,同样提供训练和测试模式(具体配置见下方参数配置即可)

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. 运行参数：</b>配置系统模式，运行频率，设备等参数
      </div>
      </br>

    * :code:`--workers(int)=35` : 环境并行训练的数量数(需要根据实际计算机的内存/显存来决定)
    * :code:`--train_mode(int)=1` : 配置运行模式是否为训练模式( :code:`--train_mode=1` 是训练模式，:code:`--train_mode=0` 是测试模式)
    * :code:`--port(int)=-1` : 环境端与算法端通信端口，默认 :code:`--port=-1` 则随机利用一个当前可用的端口，**不建议手动修改**
    * :code:`--New_Train(bool)=False` : 是否开启全新的训练，默认为 :code:`--New_Train=False`，则会加载 :code:`params.pth` 预训练权重(如果存在)进行训练，并且tensorboard的曲线也会从上一次训练曲线后加载

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. 环境参数：</b>配置选择的环境
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : 配置训练/测试环境场景种类，从 :code:`./Webots_Simulation/traffic_project/worlds/*.wbt` 中选择
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. 模型参数：</b>配置模型权重导入和保存相关参数
      </div>
      </br>

    * :code:`--savepath(str)="params.pth"` : 模型保存的路径

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. 可视化参数：</b>配置可视化文件相关参数
      </div>
      </br>

    * :code:`--tensorboard_port(int)=1` : 是否使用tensorboard-logger, :code:`--tensorboard_port(int)!=-1` 则随机分配可用端口，否则不启用(测试状态不启用)


代码封装与改动细节
~~~~~~~~~~~~~~~~~~~~~~~~~

    D-VAT采用Actor-Critic非对称框架，Actor-Critic对称架构和非对称架构的示意图如下：

    .. figure:: ../_static/image/sym_asym.png
        :alt: Asymmetric_and_Symmetrical_Structure
        :width: 700px
        :align: center

        Actor-Critic对称架构和非对称架构的示意图


    D-VAT代码主要有下述实现：

    1. 自主实现环境类

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            环境类仿照<a href="./Environment.html#gym">Gym环境类</a>自主实现<code>DVAT_ENV</code>环境类，具体代码见<code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_envs.py</code><br>
            为支持Actor-Critic非对称架构，<code>DVAT_ENV</code>环境类状态空间包括<code>actor_obs</code> 和 <code>critic_obs</code>两部分：
        </div>
        </br>

    .. code:: python

        self.observation_space = gymnasium.spaces.Dict({
            "actor_obs": gymnasium.spaces.Box(low=0, high=1.0, shape=(obs_buffer_len,)+image_shape, dtype=np.float32),
            "critic_obs": gymnasium.spaces.Box(low=-np.inf, high=np.inf, shape=(9,), dtype=np.float32),
        })


    2. 自主实现的Policy

    为支持Actor-Critic非对称架构，继承 **Tianshou** 中 :code:`DiscreteSACPolicy` 实现了 :code:`DVAT_SACDPolicy`。

    3. 自主实现并行类与Collector
    
    参考 `Async_SubprocVecEnv & SubprocVecEnv_TS <Environment.html#part3-async-subprocvecenv-subprocvecenv-ts>`_ 实现了自定义的并行环境类和collector。




log文件
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            tensorboard-logger文件见文件夹 <code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_logs</code>
        </div>
        </br>

    * 在模型训练的过程中，只要参数 :code:`--tensorboard_port(int)!=-1` ，那么启动程序时会自动启动tensorboard-logger
    * 但如果希望手动启动tensorboard，也可以使用以下的命令：

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
        具体代码见 <code>Alg_Base/DAT_Benchmark/models/R_VAT</code>文件夹
    </div>
    </br>

快速运行程序
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # 测试模式
    # 使用 累计奖励 CR 进行测试
    python ./models/R_VAT/RPPO.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode CR
    # 使用 追踪成功比例 TSR 进行测试
    python ./models/R_VAT/RPPO.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # 新训练模式
    python ./models/R_VAT/RPPO.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # 中断重开训练模式
    python ./models/R_VAT/RPPO.py -w 35 -m citystreet-day.wbt --train_mode 1

程序入口
~~~~~~~~~~~~~~~~~~~~~~~~~

    :code:`RVAT.py` 为整个程序的入口,同样提供训练和测试模式(具体配置见下方参数配置即可)

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>1. 运行参数：</b>配置系统模式，运行频率，设备等参数
      </div>
      </br>

    * :code:`--workers(int)=35` : 环境并行训练的数量数(需要根据实际计算机的内存/显存来决定)
    * :code:`--train_mode(int)=1` : 配置运行模式是否为训练模式( :code:`--train_mode=1` 是训练模式，:code:`--train_mode=0` 是测试模式)
    * :code:`--port(int)=-1` : 环境端与算法端通信端口，默认 :code:`--port=-1` 则随机利用一个当前可用的端口，不建议手动修改
    * :code:`--New_Train(bool)=False` : 是否开启全新的训练，默认为 :code:`--New_Train=False`，则会加载 :code:`params.pth` 预训练权重(如果存在)进行训练，并且tensorboard的曲线也会从上一次训练曲线后加载

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>2. 环境参数：</b>配置选择的环境
      </div>
      </br>

    * :code:`--map(str)="citystreet-day.wbt"` : 配置训练/测试环境场景种类，从 :code:`./Webots_Simulation/traffic_project/worlds/*.wbt` 中选择
    
    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>3. 模型参数：</b>配置模型权重导入和保存相关参数
      </div>
      </br>

    * :code:`--savepath(str)="params.pth"` : 模型保存的路径

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            <b>4. 可视化参数：</b>配置可视化文件相关参数
      </div>
      </br>

    * :code:`--tensorboard_port(int)=1` : 是否使用tensorboard-logger, :code:`--tensorboard_port(int)!=-1` 则随机分配可用端口，否则不启用(测试状态不启用)


课程学习
~~~~~~~~~~~~~~~~~~~~~~~~~

    * 我们的方法在RPPO的基础上增加了课程学习方法，课程学习的第一阶段，智能体会在简单的设定下（无遮挡情况，车仅直行）对颜色随机的车进行跟踪
    * 为了便于操作，我们将简单的设定抽离成地图，即 :code:`./Webots_Simulation/traffic_project/worlds/simpleway-*.wbt` 地图
    * 因此，第一阶段就在对应的  :code:`simpleway-*.wbt` 上进行训练即可
    * 完成任务理解之后，即可在视觉困难的地图上进行第三阶段训练，学习复杂视觉的特征
    * 例如，对于地图 :code:`citystreet-day.wbt` 我们三阶段的运行命令如下：

    .. code:: bash

        cd Alg_Base/DAT_Benchmark/
        # Stage1:任务理解
        python ./models/R_VAT/RPPO.py -w 35 -m simpleway-grass.wbt --train_mode 1 --New_Train
        # Stage2:视觉泛化
        python ./models/R_VAT/RPPO.py -w 35 -m citystreet-day.wbt --train_mode 1
        # 测试模式
        # 使用 累计奖励 CR 进行测试
        python ./models/R_VAT/RPPO.py -w 1 -m citystreet-night.wbt --train_mode 0 --Test_Mode CR
        # 使用 追踪成功比例 TSR 进行测试
        python ./models/R_VAT/RPPO.py -w 1 -m citystreet-night.wbt --train_mode 0 --Test_Mode TSR

.. _table-cf:

      * 两阶段地图对照表如下：

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

log文件
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            tensorboard-logger文件见文件夹 <code>Alg_Base/DAT_Benchmark/models/${model_name}_logs</code>
        </div>
        </br>

    * 在模型训练的过程中，只要参数 :code:`--tensorboard_port(int)!=-1` ，那么启动程序时会自动启动tensorboard-logger
    * 但如果希望手动启动tensorboard，也可以使用以下的命令：

    .. code:: bash

        cd Alg_Base/DAT_Benchmark/
        tensorboard --logdir models/${model_name}_logs

.. raw:: html

    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


引用：

.. [1] Luo, Wenhan, et al. "End-to-end active object tracking and its real-world deployment via reinforcement learning." IEEE transactions on pattern analysis and machine intelligence 42.6 (2019): 1317-1332.
.. [2] Dionigi, Alberto, et al. "D-VAT: End-to-End Visual Active Tracking for Micro Aerial Vehicles." IEEE Robotics and Automation Letters (2024).
.. [3] Zhong, Fangwei, et al. "Ad-vat+: An asymmetric dueling mechanism for learning and understanding visual active tracking." IEEE transactions on pattern analysis and machine intelligence 43.5 (2019): 1467-1482.



