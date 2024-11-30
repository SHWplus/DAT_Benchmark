Installation
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
        This document primarily provides installation guidance for projects on both <code>Linux</code> systems (<code>Ubuntu22.04</code>) and <code>Windows</code> systems.
    </div>
    </br>

Linux(Ubuntu22.04)
------------------------

.. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            The reason for choosing <code>Ubuntu22.04</code> is that the simulation engine we use, <code>webots2023b</code>, is compatible with the Linux system version <code>Ubuntu22.04</code>.
            If you have installed another version of Linux, you can refer to the <a href="https://github.com/cyberbotics/webots">webots</a> code repository to download and configure the appropriate version.
      </div>
      </br>

Step1 Install the Webots simulation software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Download the deb package of webots 2023b version (e.g., :code:`webots-R2023b-x86-64.deb`) and the asset files (:code:`assets-R2023b.zip`) from `webots <https://github.com/cyberbotics/webots>`_, and install them using the following command:

    **Webots Installation**

    .. code:: bash
        
        ## install
        sudo dpkg -i webots_2023b_amd64.deb

        ## run
        webots

    **Asset Decompression**

    .. code:: bash
        
        mkdir -p ~/.cache/Cyberbotics/Webots/assets/

        cp ~/Downloads/assets-R2023b.zip ~/.cache/Cyberbotics/Webots/assets/
        
        ## unzip
        cd ~/.cache/Cyberbotics/Webots/assets/ && unzip ./assets-R2023b.zip

Step2 Creating a Virtual Environment and Installing Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Virtual Environment Creation**

    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    **Algorithm Side**

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

    **Simulator Side**

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

Step3 Modify the Python environment for running Webots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Since the environment we are using is different from Webots' default Python environment, we need to create symbolic links for our new environment and configure it.

    .. code:: bash

        ln -s /root/miniconda3/envs/uav_follow311/bin/python3.11 /usr/bin/python311

    Next, open the webots software, go to :code:`Tools` -> :code:`Preferences`, and modify the option :code:`Python command` as shown in the following image:

    .. figure:: _static/image/Python_Command.png
      :alt: Python command配置                               
      :width: 600px                                              
      :align: center

      Python command config  


Windows
------------------------

.. raw:: html

    <div style="border-left: 4px solid #FA8072; padding-left: 10px; margin-left: 0;">
        <b>Note:</b> Although this project has been tested and can run on Windows systems, due to the relatively complex compilation and installation process of related cpp libraries, it is <b>not recommended</b> to use Windows systems!
    </div>
    </br>

Step1 Install Webots Simulation Software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    1. Download the webots 2023b version installer ( :code:`.exe` file) and the asset file ( :code:`assets-R2023b.zip` ) from `webots <https://github.com/cyberbotics/webots>`_.
    
    2. Copy the assets to the specified path: :code:`C:/Users/<USER>/AppData/Local/Cyberbotics/Webots/cache/assets` Then open Webots. If the environment displays correctly during the tour guide stage for new users, the installation is complete.

Step2 Create Virtual Environment and Install Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    **Virtual Environment Creation**


    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    **Algorithm Side**

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

    **Emulator Side**

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            1. Installation of Python libraries
      </div>
      </br>

    .. code:: bash

        ## Simulator requirements
        conda activate uav_follow311
        pip install lxml pyproj shapely webcolors configparser --user
        pip install transform3d

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            2. C++ Library Installation (If recompilation of the C++ code is not needed, this can be ignored)
      </div>
      </br>

    
    * First, download the latest version of the :code:`Eigen3` library from the official website `eigen <https://eigen.tuxfamily.org/index.php?title=Main_Page>`_.
    * Download and install the latest version of the :code:`Eigen3` library. `Eigen download link <https://eigen.tuxfamily.org/index.php?title=Main_Page>`_
    * Download and install the latest version of the :code:`nlohmann-json3` library. `nlohmann-json3 download link <https://github.com/nlohmann/json/tree/develop>`_

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            3. Webots' <code>makefile</code> configuration (can be ignored if the C++ part does not need to be recompiled)
      </div>
      </br>
    

    .. raw:: html

        <div style="border-left: 4px solid #d3d3d3; padding-left: 10px; margin-left: 0;">
            Paths of makefile files that need to be modified include:
            <code>Webots_Simulation/traffic_project/controllers/drone_ctrl2/Makefile</code>
            <code>Webots_Simulation/traffic_project/controllers/simpleCar_ctrl/Makefile</code>
        </div>
        </br>
        
    Since the Linux system generally does not require additional settings for include paths, a check for the Windows system has been made. If it is a Windows system, you need to manually modify the makefile of the drone_ctrl2 and simpleCar_ctrl controllers, adding the include paths for eigen and nlohmann_json.

        .. code:: make

            null :=
            space := $(null) $(null)
            WEBOTS_HOME_PATH?=$(subst $(space),\ ,$(strip $(subst \,/,$(WEBOTS_HOME))))
            ifeq ($(OS),Windows_NT)
                INCLUDE += -I D:/cppLibrary/include/Eigen3/include/eigen3
                INCLUDE += -I D:/cppLibrary/include/nlohmann_json/include
            endif
            include $(WEBOTS_HOME_PATH)/resources/Makefile.include

        * Among them, :code:`INCLUDE += -I D:/cppLibrary/include/Eigen3/include/eigen3` needs to be configured as the path to the :code:`Eigen3` library.
        * :code:`INCLUDE += -I D:/cppLibrary/include/nlohmann_json/include` needs to be configured to the path of the :code:`nlohmann-json3` library.
        * After completing the above modifications, you can open the controller in the Webots editor and recompile it.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            4. Install <code>sumo</code>
      </div>
      </br>


    * Follow the instructions in the `sumo-interface.md <https://github.com/cyberbotics/webots/blob/master/docs/automobile/sumo-interface.md>`_ document for installation.

    .. raw:: html

      <div style="background-color: #e5f1fe; padding: 15px; border-radius: 5px; border: 1px solid #1874CD;">
            5. <code>webots</code> and <code>sumo</code> environment variable configuration
      </div>
      </br>

    * First, press :code:`WIN+R` to bring up the Run window, then type :code:`sysdm.cpl` to open the System Properties page. Next, select "Advanced" -> "Environment Variables" -> "System variables" -> "New".
    * Insert :code:`SUMO_HOME` configured as shown in the following figure:

        .. figure:: _static/image/SUMO_HOME.png
            :alt: SUMO_HOME configuration                               
            :width: 600px                                              
            :align: center

            SUMO_HOME Configuration

    * Insert :code:`WEBOTS_HOME` and configure it as shown in the figure below:

        .. figure:: _static/image/WEBOTS_HOME.png
            :alt: WEBOTS_HOME configuration                               
            :width: 600px                                              
            :align: center

            WEBOTS_HOME configuration

Step3 Modify the Python environment for running Webots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * In Linux systems, the issue is resolved by adding a symbolic link, while in Windows, the running path is directly inserted into webots.

    * Enter the webots software, select :code:`Tools` -> :code:`Preferences`, and modify the :code:`Python command` option as shown in the figure below:

    .. figure:: _static/image/Python_CommandWIN.png
        :alt: Python_CommandWIN configuration                               
        :width: 600px                                              
        :align: center

        Python_Command(Windows) configuration


Docker
------------------------

Step1 Download Webots and Create Docker Container to Run with GPU
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Create Workspace and Download Webots

    .. code:: bash

        ## Create Workspace
        mkdir Workspace
        cd Workspace/
        git clone https://github.com/cyberbotics/webots-docker.git

    * Create Docker Container and Run with GPU

    .. code:: bash

        sudo docker run --gpus "device=0" --privileged=true -p 5900:5900 -p 7787:7787 -p 6006:6006 -it cyberbotics/webots:latest /bin/bash


Step2 Creating a Virtual Environment and Installing Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Virtual Environment Creation:

    .. code:: bash

        conda create -n uav_follow311 python=3.11
        conda activate uav_follow311

    * Algorithm Side:

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

    * Simulator Side:

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

    * Add Python symbolic Links:

    .. code:: bash

        ## Create symbolic link for algorithm side Python
        ln -s /root/miniconda3/envs/uav_follow_alg311/bin/python3.11 /usr/bin/python311
        ## Create symbolic link for simulation side Python
        ln -s /root/miniconda3/envs/uav_follow311/bin/python3.11 /usr/bin/python311
        mv /usr/bin/python3.10 /usr/

Step3 Configure Project Workspace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    * Download Project

    .. code:: bash

        ## Clone project
        mkdir /usr/local/Github_Project
        cd /usr/local/Github_Project
        git clone ${github_link}

    * run webots simulation

    .. code:: bash

        ## Run simulation initialization code, ensure the program completes initialization before proceeding
        conda activate uav_follow311
        xvfb-run -a webots --stdout --stderr --no-rendering --batch --mode=fast ${map_file}
        ps aux | grep xvfb
        x11vnc -display :99 -auth ***

    * Configure Algorithm Side

    .. code:: bash

        cd /usr/local/Github_Project/UAV_Follow_Env/Alg_Base/DAT_Benchmark/
        python311 ${main_path}

    .. raw:: html

      <div style="background-color: #FDF5E6; padding: 15px; border-radius: 5px; border: 1px solid #EEC591;">
            Here, the path for ${main_path} can be found in: <a href=".\Algorithm\Introduction.html">Introduction to the Algorithm Section</a>
      </div>
      </br>
