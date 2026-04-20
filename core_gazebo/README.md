# ASTRA Core Gazebo Sim

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

This package contains the launch file and configuration to simulate Core in Gazebo.

## Table of Contents

- [Software Prerequisites](#software-prerequisites)
- [Usage](#usage)
  - [Setup](#setup)
  - [Running](#running)
- [How it Do](#how-it-do)
- [Maintainer(s)](#maintainers)

## Software Prerequisites

You need either [ROS2 Humble](https://docs.ros.org/en/humble/Installation.html) with [rosdep](https://docs.ros.org/en/humble/Tutorials/Intermediate/Rosdep.html#rosdep-installation) or [Nix](https://nixos.org/download/#nix-install-linux) installed. We have not confirmed functionality on Nix or ROS2 Jazzy, so for now I (David) can only offer support with ROS2 Humble on Jammy.

## Usage

### Setup

#### Nix

With Nix, all you have to do is enter the development shell:

```bash
$ cd rover-ros2
$ nix develop
```

#### ROS2 Humble + rosdep

With ROS2 Humble, start by using rosdep to install dependencies:

```bash
  # Setup rosdep (if not already ran):
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

The full Gazebo simulation stack can be launched with the following command:

```bash
$ ros2 launch core_gazebo core.gazebo.launch.py
```

If you need camera output, the following command will also publish a simulated camera on `/camera_head/*`:

```bash
$ ros2 launch core_gazebo core.gazebo.launch.py use_camera:=True
```

To drive Clucky, either run headless with `--ros-args -p use_old_topics:=False -p use_cmd_vel:=True` (run Anchor with the mock connector to satisfy the start condition in Headless), or run the following command to use your keyboard:

```bash
$ ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/diff_controller/cmd_vel -p stamped:=true
```

## How it Do

The launch file uses the following nodes and other launch files:

- **robot_state_publisher.launch.py** - Located in `core_description`, publishes the Core URDF on /robot_description and publishes TF data from the joint states provided by either `joint_state_publisher_gui` (for display.launch.py) or Gazebo, and launches RViz to display TF data.
- **controller_manager** - spawns the necessary ros2 controllers (`joint_broacaster` and `diff_controller`) for Gazebo to translate `/cmd_vel` into wheel velocities and translates JointStates from `joint_broadcaster` into TF data and basic dead reckoned odometry.
- **gz_sim.launch.py** - Launches Gazebo Ignition itself.
- **ros_gz_bridge** - Bridges messages between Gazebo topics (`gz topic -l`) and ROS2 topics (`ros2 topic list`).
- **ros_gz_sim create** - Spawns the Core URDF inside Gazebo using `/robot_description`.

## Maintainer(s)

| Name | Email | Discord |
| ---- | ----- | ------- |
| David Sharpe | ds0196@uah.edu | ddavdd |
