概述
=================

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
                window.location.href = 'Overview.html';
            } else if (lang === 'en') {
                window.location.href = '../en/Overview.html';
            }
        }
    </script>
    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>


1 主动视觉跟踪
------------------------------------

VAT 任务
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **现实任务**：在现实视觉任务中，目标具有高动态特性，主动控制相机以提升视觉准确率是主要挑战。
* **现有方法**：现有 PVT(Passive Visual Tracking)方法基于目标在预设镜头内的假设，仅在视频中进行跟踪。
* **VAT任务**：VAT(Visual Active Tracking)同时建模视觉跟踪和控制，做到主动控制相机以追踪动态目标，更具现实意义。

.. figure:: ./_static/image/VisualActiveTracking.png
   :alt: Visual Active Tracking
   :width: 600px
   :align: center

   VAT任务与PVT设定区别

.. raw:: html

    </br>

VAT 方案
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **现有VAT方案**: 直接串联目标跟踪模型与控制模型进行VAT(如：siamask+PID)

   **局限1**: 视觉模型需要大量人力进行标签批注

   **局限2**: 控制模型对于参数敏感，需要对于每个不同场景进行参数微调

* **本项目 VAT 方案**: 利用MDP(Markov Decision Process)同时对于视觉与控制任务进行建模，用单模型解决视觉与控制任务

   **优势**：端到端RL效率更高、更适合跨场景任务

.. figure:: ./_static/image/1_2stages.png
   :alt: VAT Model
   :width: 600px
   :align: center

   单阶段与两阶段VAT方案示意图

2 Benchmark呈现
------------------------------------

.. _DAT 的统计和仿真器元素示意图:

.. figure:: ./_static/image/statistics.png
   :alt: VAT Model
   :width: 600px
   :align: center

   DAT 的统计和仿真器元素示意图

场景复杂多样
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * **场景设置多样**：具备6种场景4种天气共计24个环境，如图 :ref:`24个开放场景示意图` 所示。

   * **场景元素复杂**：从7个方面构建真实场景的复杂性，包含场景面积(:math:`km^{2}`)、建筑物密度(:math:`km^{-2}`)、颜色丰富度、道路密度(:math:`km^{-2}`)、地形密度(:math:`km^{-2}`)、树木密度(:math:`km^{-2}`)和隧道密度(:math:`km^{-2}`)。6场景统计信息见上图 (a) 所示，困难元素如上图 (b) 所示。
     具体来说，场景面积是指场景的范围，建筑密度是建筑数量与场景面积的比率，色彩丰富度是场景中主要色彩的数量。这三个方面主要描绘了视觉背景的复杂性。道路密度是通过评估转弯、交叉口和人行横道等复杂元素的密度来测量的，而地形密度是通过估算场景中山脉等特殊地形特征的密度来确定的。这两个方面主要描述了跟踪目标行为的复杂性。此外，树木密度和隧道密度分别为树木和隧道数量与场景面积的比率，用于测量场景内的视觉遮挡水平。


.. _24个开放场景示意图:

.. figure:: ./_static/image/24Scene_Colorful2.png
   :alt: 24 Scenes
   :width: 600px
   :align: center

   24个开放场景示意图

跟踪器与目标丰富多元
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * **Tracker多样**：可选择地面机器人与无人机作为Tracker，支持地面机器人自主模型接入

   * **Target多样**：预设24种可选target,支持自主模型接入，如图 :ref:`DAT 的统计和仿真器元素示意图` 中 (d) 所示，详见：:ref:`追踪对象`

   * **行为管理真实丰富**：接入交通仿真器SUMO以统一管理车辆， 确保环境中的Target行为的真实性和随机性

任务设置自由灵活
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * **多传感器**：提供6种常见视觉和运动传感器，如图 :ref:`DAT 的统计和仿真器元素示意图` 中 (c) 所示

   * **任务设置自定义**：提供附加参数用于reward设计及任务拓展，参数详见 :ref:`定制化参数接口`

