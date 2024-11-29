安装
=============

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
                window.location.href = '../zh/Installation.html';
            } else if (lang === 'en') {
                window.location.href = '../en/Installation.html';
            }
        }
    </script>
    </br>
    <hr style="border: 2px solid #d3d3d3; width: 95%; margin: 10px auto;">
    </br>
    </br>

.. raw:: html

    <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
        本文档主要提供 <code>Linux</code>系统(<code>Ubuntu22.04</code>)，<code>Windows</code>系统及利用docker容器的工程安装指引
    </div>
    </br>

Linux(Ubuntu22.04)
------------------------

.. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            选择<code>Ubuntu22.04</code>是由于我们使用的仿真引擎<code>webots2023b</code>适配的Linux系统版本为<code>Ubuntu22.04</code>
            如果安装了其他版本的Linux系统，可以参考 <a href="https://github.com/cyberbotics/webots">webots</a>的代码仓库下载配置合适的版本
      </div>
      </br>

Step1 安装webots仿真软件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    从 `webots <https://github.com/cyberbotics/webots>`_ 下载webots2023b版本的deb包(例如： :code:`webots-2023b-x86-64.deb` )和资产文件( :code:`assets-R2023b.zip` )，使用如下命令安装:

    **webots安装**

    .. code:: bash
        
        ## install
        sudo dpkg -i webots_2023b_amd64.deb

        ## run
        webots

    **assets解压**

    .. code:: bash
        
        mkdir -p ~/.cache/Cyberbotics/Webots/assets/

        cp ~/Downloads/assets-R2023b.zip ~/.cache/Cyberbotics/Webots/assets/
        
        ## unzip
        cd ~/.cache/Cyberbotics/Webots/assets/ && unzip ./assets-R2023b.zip

Step2 创建虚拟环境与库安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **虚拟环境创建**

    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    **算法端**

    .. code:: bash

        ## Alg requirements
        pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu121
        pip install numpy==1.25.0
        pip install opencv-python==4.9.0.80
        pip install gym==0.25.1
        pip install setproctitle==1.3.3
        pip install tensorboard
        pip install tqdm
        pip install stable-baselines3==2.3.0
        pip install sb3_contrib==2.3.0
        pip install gymnasium
        pip install wandb==0.17.6
        pip install memory_profiler==0.61.0
        pip install psutil==6.0.0
        pip install pandas
        pip install openpyxl
        pip install tianshou==1.1.0

    **仿真器端**

    .. code:: bash

        ## Simulator requirements
        sudo apt-get install libeigen3-dev
        sudo apt-get install nlohmann-json3-dev

        sudo apt install sumo sumo-tools sumo-doc
        pip install lxml pyproj shapely webcolors configparser --user
        pip install transforms3d

        ## config
        gedit ~/.bashrc
        # Change dir according to your installation
        export SUMO_HOME=/usr/share/sumo
        export WEBOTS_HOME=/usr/local/webots

Step3 修改webots运行python环境
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    由于我们使用的环境与webots本身默认的python环境不相同，因此需要为我们新的环境创建软链接并进行配置

    .. code:: bash

        sudo ln -s ~/anaconda3/envs/uav_follow311/bin/python3.11 /usr/bin/python311

    接着进入webots软件，选择 :code:`工具(Tools)` -> :code:`首选项(Preferences)`, 按照如下图将选项 :code:`Python command` 进行修改：

    .. figure:: _static/image/Python_Command.png
      :alt: Python command配置                               
      :width: 600px                                              
      :align: center

      Python command配置  


Windows
------------------------

.. raw:: html

    <div style="border-left: 4px solid #FA8072; padding-left: 10px; margin-left: 0;">
        <b>注意：</b>虽然本工程经过测试能够在Windows系统下运行，但由于相关cpp库的编译安装流程相对复杂，因此<b>不建议</b>使用Windows系统！
    </div>
    </br>

Step1 安装webots仿真软件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. 从 `webots <https://github.com/cyberbotics/webots>`_ 下载webots2023b版本安装器( :code:`.exe` 文件)和资产文件( :code:`assets-R2023b.zip` )。
    
    2. 将资产复制到指定路径： :code:`C:/Users/<USER>/AppData/Local/Cyberbotics/Webots/cache/assets` 接着打开webots，如果新用户在tour guide阶段能正常显示环境，则说明安装完成。

Step2 创建虚拟环境与库安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **虚拟环境创建**

    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    **算法端**

    .. code:: bash

        ## Alg requirements
        pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu121
        pip install numpy==1.25.0
        pip install opencv-python==4.9.0.80
        pip install gym==0.25.1
        pip install setproctitle==1.3.3
        pip install tensorboard
        pip install tqdm
        pip install stable-baselines3==2.3.0
        pip install sb3_contrib==2.3.0
        pip install gymnasium
        pip install wandb==0.17.6
        pip install memory_profiler==0.61.0
        pip install psutil==6.0.0
        pip install pandas
        pip install openpyxl
        pip install tianshou==1.1.0

    **仿真器端**

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            1. python库安装
      </div>
      </br>

    .. code:: bash

        ## Simulator requirements
        conda activate uav_follow311
        pip install lxml pyproj shapely webcolors configparser --user
        pip install transform3d

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            2. C++ 库安装(如不需要重新编译C++部分代码，可忽略)
      </div>
      </br>

    
    * 首先在 `eigen <https://eigen.tuxfamily.org/index.php?title=Main_Page>`_ 官网下在最新版本的 :code:`Eigen3` 库
    * 下载最新版本的 :code:`Eigen3` 库并编译安装。 `eigen下载链接 <https://eigen.tuxfamily.org/index.php?title=Main_Page>`_ 
    * 下载最新版本的 :code:`nlohmann-json3` 库并编译安装。 `nlohmann-json3下载链接 <https://github.com/nlohmann/json/tree/develop>`_ 

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            3. webots的<code>makefile</code>配置(若不需要重新编译C++部分代码，可忽略)
      </div>
      </br>
    

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            需要修改的makefile文件路径包括： 
            <code>Webots_Simulation/traffic_project/controllers/drone_ctrl2/Makefile</code>
            <code>Webots_Simulation/traffic_project/controllers/simpleCar_ctrl/Makefile</code>
        </div>
        </br>
        
    由于linux系统一般不需要额外设置包含路径，因此做了windows系统的判断，如果是windows系统需要手动修改drone_ctrl2和simpleCar_ctrl控制器的makefile，添加eigen以及nlohmann_json的包含路径

        .. code:: make

            null :=
            space := $(null) $(null)
            WEBOTS_HOME_PATH?=$(subst $(space),\ ,$(strip $(subst \,/,$(WEBOTS_HOME))))
            ifeq ($(OS),Windows_NT)
                INCLUDE += -I D:/cppLibrary/include/Eigen3/include/eigen3
                INCLUDE += -I D:/cppLibrary/include/nlohmann_json/include
            endif
            include $(WEBOTS_HOME_PATH)/resources/Makefile.include

        * 其中， :code:`INCLUDE += -I D:/cppLibrary/include/Eigen3/include/eigen3` 需要配置成 :code:`Eigen3` 库的路径
        *  :code:`INCLUDE += -I D:/cppLibrary/include/nlohmann_json/include` 需要配置成 :code:`nlohmann-json3` 库的路径
        * 完成上述修改后就可以进入webots编辑器打开控制器并进行重新编译了

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            4. 安装 <code>sumo</code>
      </div>
      </br>


    * 按照文档 `sumo-interface.md <https://github.com/cyberbotics/webots/blob/master/docs/automobile/sumo-interface.md>`_ 进行安装即可

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            5. <code>webots</code> 和 <code>sumo</code> 环境变量配置
      </div>
      </br>

    * 首先 :code:`WIN+R` 调出运行窗,再输入 :code:`sysdm.cpl` 调出系统属性页面，接着选择“高级”->“环境变量”->“系统变量”->“新建”
    * 插入 :code:`SUMO_HOME` 按照下图方式进行配置：

        .. figure:: _static/image/SUMO_HOME.png
            :alt: SUMO_HOME配置                               
            :width: 600px                                              
            :align: center

            SUMO_HOME配置

    * 插入 :code:`WEBOTS_HOME` 按照下图方式进行配置：

        .. figure:: _static/image/WEBOTS_HOME.png
            :alt: WEBOTS_HOME配置                               
            :width: 600px                                              
            :align: center

            WEBOTS_HOME配置

Step3 修改webots运行python环境
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Linux系统下通过添加软链接的方式解决，而在Windows下直接将运行路径插入webots中

    * 进入webots软件，选择 :code:`工具(Tools)` -> :code:`首选项(Preferences)`, 按照如下图将选项 :code:`Python command` 进行修改：

    .. figure:: _static/image/Python_CommandWIN.png
        :alt: Python_CommandWIN配置                               
        :width: 600px                                              
        :align: center

        Python_Command(Windows)配置

Docker
------------------------

Step1 下载Webots并创建docker容器并运行gpu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * 创建工作空间并下载Webots

    .. code:: bash

        ## 创建工作空间
        mkdir Workspace
        cd Workspace/
        git clone https://github.com/cyberbotics/webots-docker.git

    * 创建docker容器并运行gpu

    .. code:: bash

        sudo docker run --gpus "device=0" --privileged=true -p 5900:5900 -p 7787:7787 -p 6006:6006 -it cyberbotics/webots:latest /bin/bash


Step2 创建虚拟环境与库安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * 虚拟环境创建：

    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    * 算法端：

    .. code:: bash
        
        ## Alg requirements
        pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cu121
        pip install numpy==1.25.0
        pip install opencv-python==4.9.0.80
        pip install gym==0.25.1
        pip install setproctitle==1.3.3
        pip install tensorboard
        pip install tqdm
        pip install stable-baselines3==2.3.0
        pip install sb3_contrib==2.3.0
        pip install gymnasium
        pip install wandb==0.17.6
        pip install memory_profiler==0.61.0
        pip install psutil==6.0.0
        pip install pandas
        pip install openpyxl
        pip install tianshou==1.1.0

    * 仿真器端：

    .. code:: bash
        
        ## Simulator requirements
        sudo apt-get install libeigen3-dev
        sudo apt-get install nlohmann-json3-dev

        sudo apt install sumo sumo-tools sumo-doc
        pip install lxml pyproj shapely webcolors configparser --user
        pip install transforms3d

        ## config
        gedit ~/.bashrc
        # Change dir according to your installation
        export SUMO_HOME=/usr/share/sumo
        export WEBOTS_HOME=/usr/local/webots

    * 添加 pyhton 软链接:

    .. code:: bash

        ## Create symbolic link for algorithm side Python
        ln -s /root/miniconda3/envs/uav_follow_alg311/bin/python3.11 /usr/bin/python311
        ## Create symbolic link for simulation side Python
        ln -s /root/miniconda3/envs/uav_follow311/bin/python3.11 /usr/bin/python311
        mv /usr/bin/python3.10 /usr/


Step4 配置项目工作
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * 下载工程项目

    .. code:: bash

        ## clone项目工程
        mkdir /usr/local/Github_Project
        cd /usr/local/Github_Project
        git clone ${github_link}

    * 启动webots仿真

    .. code:: bash

        #开启仿真端代码，一定要等程序完成初始化之后再运行下面的步骤
        conda activate uav_follow311
        xvfb-run -a webots --stdout --stderr --no-rendering --batch --mode=fast ${map_file}
        ps aux | grep xvfb
        x11vnc -display :99 -auth ***

    * 算法端配置

    .. code:: bash

        cd /usr/local/Github_Project/UAV_Follow_Env/Alg_Base/DAT_Benchmark/
        python311 ${main_path}

    .. raw:: html

        <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
        此处 ${main_path}路径参考: <a href=".\Algorithm\Introduction.html">算法部分介绍</a>
        </div>
        </br>
