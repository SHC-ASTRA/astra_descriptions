# ASTRA Rover Description Files

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Contains URDF files, meshes, launch files, and configurations for Clucky and Testbed.

## Table of Contents

- [Software Prerequisites](#software-prerequisites)
- [Usage](#usage)
  - [Setup](#setup)
  - [Running](#running)
  - [Gazebo](#gazebo)
- [Packages](#packages)
- [Major To-Do Items](#major-to-do-items)
- [Maintainer(s)](#maintainers)

## Software Prerequisites 

You need either [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html) with [rosdep](https://docs.ros.org/en/humble/Tutorials/Intermediate/Rosdep.html#rosdep-installation) or [Nix](https://nixos.org/download/#nix-install-linux) installed. Only ROS2 Humble on Jammy is currently supported, but `ros2 launch <*_description> display.launch.py` commands should be fully functional on Nix (with [NixGL](https://github.com/nix-community/nixGL?tab=readme-ov-file#directly-run-nixgl) if not on NixOS).

Uses [ros2_control](https://control.ros.org/humble/index.html), [Moveit2](https://moveit.picknik.ai/main/index.html), and [Gazebo Ignition Fortress](https://gazebosim.org/docs/fortress/getstarted/) (NOT [Classic](https://classic.gazebosim.org/)).

## Usage

### Setup

#### Nix

With Nix, all you have to do is enter the development shell:

```bash
$ cd rover-ros2
$ nix develop
```

#### ROS2 Humble + rosdep

With ROS2 Humble on Ubuntu Jammy, start by using rosdep to install dependencies:

```bash
  # Setup rosdep (if not already):
$ sudo rosdep init
$ rosdep update
  # Install dependencies:
$ cd rover-ros2  # or whatever workspace you are using
$ rosdep install --from-paths src -y --ignore-src
```

Next, build and source the workspace:

```bash
$ colcon build  # recommended flag for developers: --symlink-install
$ source install/setup.bash  # or if you are using zsh: install/setup.zsh
```

### Running

Here are the main launch commands for these packages:

```bash
$ ros2 launch core_description display.launch.py  # View Core URDF in RViz
$ ros2 launch arm_description display.launch.py   # View Arm URDF in RViz
$ ros2 launch core_gazebo core.gazebo.launch.py   # Simulate Clucky in Gazebo with diff_drive_controller
$ ros2 launch arm_moveit_config demo.launch.py    # Run Moveit2 for Arm IK
```

### Gazebo

This repository contains a Dockerfile that can be used to run Gazebo on non-Ubuntu systems (e.g., NixOS). It uses `ros:humble-ros-desktop` as a base image and `rosdep` for setting up dependencies. To use it, simply run:

```bash
$ src/astra_descriptions/gazebo/run_container.sh
```

This will build (if necessary) and run the container, dropping you into a bash shell. Your local copy of `astra_descriptions` will be volume mounted into the container, and the workspace has already been built using symlinks. The script will recommend that you run the following command to launch a Gazebo simulation with Core:

```bash
$ source install/setup.bash && ros2 launch core_gazebo core.gazebo.launch.py
```

## Packages

- **arm_description** - Includes a URDF file, meshes, and launch files for Arm.
- **arm_moveit_config** - Includes configuration and launch files for using Moveit2 with the astra arm.
- **core_description** - Includes URDF/Xacro files, launch files, and configurations for Core (Clucky, not Testbed).
- **core_gazebo** - Configuration and launch files for simulating Clucky with Gazebo.

## Major To-Do Items

- Reduce STL file complexity
- Add proper textures to Core and Arm
- Convert Arm to fully Xacro

## Maintainer(s)

| Name | Email | Discord |
| ---- | ----- | ------- |
| David Sharpe | ds0196@uah.edu | ddavdd |