算法部分介绍
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
                    window.location.href = 'Introduction.html';
                } else if (lang === 'en') {
                    window.location.href = '../../en/Algorithm/Introduction.html';
                }
            }
        </script>
        </br>
        <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
        </br>
        </br>    

    .. raw:: html

      <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
            本项目提供了<b>3种环境类的实现，以及3种baseline算法</b>，可供用户后续进行算法设计和性能比较
            环境类详细文档参考: <a href="Environment.html">环境封装</a> ；算法类详细文档参考： <a href="Model.html">模型搭建</a> 
      </div>
      </br>

快速开始(运行baseline算法)
---------------------------

Baseline1: :code:`BenchEnv_Multi` 环境 +  :code:`A3CLSTM-E2E` 算法 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        环境代码见 <code>Alg_Base/DAT_Benchmark/envs/environment.py</code>
        算法代码见 <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E/</code>
    </div>
    </br>


可以运行如下代码快速开启算法：

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

Baseline2: :code:`UAV_VAT_Gymnasium` 环境 +  :code:`D-VAT` 算法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        环境代码见 <code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_envs.py</code>
        算法代码见 <code>Alg_Base/DAT_Benchmark/models/D_VAT/</code>
    </div>
    </br>

可以运行如下代码快速开启算法：

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

Baseline3(Ours): :code:`Envs` 环境 +  :code:`R-VAT` 算法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        环境代码见 <code>Alg_Base/DAT_Benchmark/envs/envs_parallel.py</code>
        算法代码见 <code>Alg_Base/DAT_Benchmark/models/R_VAT/</code>
    </div>
    </br>


可以运行如下代码快速开启算法：

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # 测试模式
    # 使用 累计奖励 CR 进行测试
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode CR
    # 使用 追踪成功比例 TSR 进行测试
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # 新训练模式
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # 中断重开训练模式
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1
    