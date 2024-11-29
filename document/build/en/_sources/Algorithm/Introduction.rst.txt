Algorithm Introduction
==========================

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
                    window.location.href = '../../zh/Algorithm/Introduction.html';
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
            This project provides <b>3 types of environment implementations, and 3 baseline algorithms</b> for users to design algorithms and compare their performance.
            For detailed documentation on environment classes, see: <a href="Environment.html">Environment Wrapping</a>; for detailed documentation on algorithm classes, see: <a href="Model.html">Model Construction</a>
      </div>
      </br>

Quick Start (Running baseline algorithms)
-----------------------------------------------

Baseline1: :code:`BenchEnv_Multi` environment +  :code:`A3CLSTM-E2E` algorithm 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        Environment code is located at <code>Alg_Base/DAT_Benchmark/envs/environment.py</code>
        Algorithm code is located at <code>Alg_Base/DAT_Benchmark/models/A3CLSTM_E2E/</code>
    </div>
    </br>


You can run the following code to quickly start the algorithm:

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Test using Cumulative Reward (CR)
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode AR
    # Test using Tracking Success Rate (TSR)
    python ./models/A3CLSTM_E2E/main.py --Mode 0 --Scene "citystreet" --Weather "day" --delay 20 --Test_Param "CityStreet-d" --Test_Mode TSR
    # New training mode
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125 --New_Train
    # Resuming training mode
    python ./models/A3CLSTM_E2E/main.py --Mode 1 --workers 35 --Scene "citystreet" --Weather "day" --delay 20 --Freq 125

Baseline2: :code:`UAV_VAT_Gymnasium` environment +  :code:`D-VAT` algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        Environment code can be found at <code>Alg_Base/DAT_Benchmark/models/D_VAT/DVAT_envs.py</code>
        Algorithm code can be found at <code>Alg_Base/DAT_Benchmark/models/D_VAT/</code>
    </div>
    </br>

You can run the following code to quickly start the algorithm:

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Test using Cumulative Reward (CR)
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode CR
    # Test using Tracking Success Rate (TSR)
    python ./models/D_VAT/DVAT_main.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # New training mode
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # Resume training mode
    python ./models/D_VAT/DVAT_main.py -w 35 -m citystreet-day.wbt --train_mode 1

Baseline3(Ours): :code:`Envs` Environment +  :code:`R-VAT` Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
        Environment code can be found at <code>Alg_Base/DAT_Benchmark/envs/envs_parallel.py</code>
        Algorithm code can be found at <code>Alg_Base/DAT_Benchmark/models/R_VAT/</code>
    </div>
    </br>


You can run the following code to quickly start the algorithm:

.. code:: bash

    cd Alg_Base/DAT_Benchmark/
    # Test mode
    # Test using Cumulative Reward (CR)
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode AR
    # Test using Tracking Success Rate (TSR)
    python ./models/R_VAT/RVAT.py -w 1 -m citystreet-day.wbt --train_mode 0 --Test_Mode TSR
    # New training mode
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1 --New_Train
    # Resume training mode
    python ./models/R_VAT/RVAT.py -w 35 -m citystreet-day.wbt --train_mode 1
    