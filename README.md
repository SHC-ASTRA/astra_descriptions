# ASTRA Rover Description Files
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## About
- Contains URDF files, meshes, launch files, and configurations for Clucky and Testbed.
- Included packages:
    - **arm_description** - Includes a URDF file, meshes, and launch files for Arm.
    - **arm_moveit_config** - Includes configuration and launch files for using Moveit2 with the astra arm.
    - **core_description** - Includes URDF/Xacro files, launch files, and configurations for Core (Clucky, not Testbed).
    - **core_gazebo** - Configuration and launch files for simulating Clucky with Gazebo.

# Table of Contents
1. Title
2. Table of Contents
3. Software Requirements
    1. ROS2 Humble
4. Hardware Requirements
5. Recommended Programs
6. How to Use
7. Common Problems/Troubleshooting
8. Major To-Do Items
9. Author(s) 
10. Maintainer(s)

# Software Requirements 
Since July/August of 2025, ASTRA uses NixOS. A functioning NixOS installation is assumed.

Uses [ros2_control](https://control.ros.org/humble/index.html), [Moveit2](https://moveit.picknik.ai/main/index.html), and [Gazebo Ignition Fortress](https://gazebosim.org/docs/fortress/getstarted/) (NOT [Classic](https://classic.gazebosim.org/)).

## ROS2 Humble
We use [ROS2 Humble](https://docs.ros.org/en/humble/index.html), and plan on using that until support for it expires. 

To install ROS2, run the following command in your /etc/nixos folder:
```nix
nix flake init --template github:lopsided98/nix-ros-overlay
```

# Hardware Requirements 
- A functioning computer.

# Recommended Programs

## VSCode
VSCode is a wonderful program. I used it to make this project and recommend anyone else working on it use it as well. 

To install VSCode, add the following package to your pkgs array / packages.nix config file:
```nix
vscode-fhs
```
Alternatively, use a flake to install home-manager, and add to your home.nix:
```nix
vscode.enable = true;
```

# How to Use
```bash
$ colcon build
$ source install/setup.bash
# main launch files:
$ ros2 launch core_description display.launch.py  # View Core URDF in RViz
$ ros2 launch arm_description display.launch.py  # View Arm URDF in RViz
$ ros2 launch core_gazebo core.gazebo.launch.py  # Simulate Clucky in Gazebo with diff_drive_controller
$ ros2 launch arm_moveit_config demo.launch.py  # Run Moveit2 for Arm IK
```

# Common Problems/Troubleshooting
  
- For `core.gazebo.launch.py`, sometimes the controllers do not get correctly loaded and configured.

# Major To-Do Items
- Reduce STL file complexity
- Add proper textures to Core and Arm
- Convert Arm to Xacro

# Author(s)
|Name| Email |
|--|--|
| David Sharpe | ds0196@uah.edu |

# Maintainer(s)
|Name| Email |
|--|--|
| David Sharpe | ds0196@uah.edu |