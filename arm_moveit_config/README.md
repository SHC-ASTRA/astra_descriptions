# ASTRA Arm Moveit2 Configuration

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

This package contains URDF, configuration, and launch files to support controlling the ASTRA Arm via Moveit2.

## Table of Contents

- [Software Prerequisites](#software-prerequisites)
- [Usage](#usage)
  - [Setup](#setup)
  - [Running](#running)
    - [Switching between sim and real hardware](#switching-between-sim-and-real-hardware)
- [File Structure](#file-structure)
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

ASTRA's full Moveit2 software stack as it currently stands can be invoked by running the following command:

```bash
$ ros2 launch arm_moveit_config demo.launch.py
```

#### Switching between sim and real hardware

Whether Moveit2 controls mock simulated hardware or the real arm is controlled by the state of two files: `config/ASTRA_Arm.ros2_control.xacro` and `launch/spawn_controllers.launch.py`. Work is being done to make this switching easier and more centralized, but for now, here is how you can tell which one you are using and how to switch:

- **To use mock simulated hardware:**

> `launch/spawn_controllers.launch.py` (line 35)
```py
...
def generate_launch_description():
    ...
    # * Uncomment the following when using mock_components simulation hardware
    controller_names += ["joint_state_broadcaster"]
    ...
```

> `config/ASTRA_Arm.ros2_control.xacro` (line 7)
```xml
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    ...
        <ros2_control name="${name}" type="system">
            <hardware>
                <!-- By default, set up controllers for simulation. This won't work on real hardware -->
                <plugin>mock_components/GenericSystem</plugin>
                <param name="calculate_dynamics">true</param>
                <!-- <plugin>topic_based_ros2_control/TopicBasedSystem</plugin> -->
                <!-- <param name="joint_commands_topic">/joint_commands</param> -->
                <!-- <param name="joint_states_topic">/joint_states</param> -->
                <!-- <param name="trigger_joint_command_threshold">1e-5</param> -->  <!-- Set to -1 to disable -->
                <!-- <param name="sum_wrapped_joint_states">false</param> -->
            </hardware>
            ...
```

- **To use real hardware:**

> `launch/spawn_controllers.launch.py` (line 35)
```py
...
def generate_launch_description():
    ...
    # * Uncomment the following when using mock_components simulation hardware
    # controller_names += ["joint_state_broadcaster"]
    ...
```

> `config/ASTRA_Arm.ros2_control.xacro` (line 7)
```xml
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    ...
        <ros2_control name="${name}" type="system">
            <hardware>
                <!-- By default, set up controllers for simulation. This won't work on real hardware -->
                <!-- <plugin>mock_components/GenericSystem</plugin> -->
                <!-- <param name="calculate_dynamics">true</param> -->
                <plugin>topic_based_ros2_control/TopicBasedSystem</plugin>
                <param name="joint_commands_topic">/joint_commands</param>
                <param name="joint_states_topic">/joint_states</param>
                <param name="trigger_joint_command_threshold">1e-5</param>  <!-- Set to -1 to disable -->
                <param name="sum_wrapped_joint_states">false</param>
            </hardware>
            ...
```

## File Structure

 - `config/`
   - **astra_arm_simulated_config.yaml** - Configuration related to moveit_servo (translating Twist/JointJog to JointTrajectory)
   - **ASTRA_Arm.ros2_control.xacro** - ros2_control tags for the arm's urdf
   - **ASTRA_Arm.srdf** - Provides Moveit2 some misc. information about the arm
   - **ASTRA_Arm.urdf.xacro** - Combines the URDF file from `arm_description` and Moveit's xacro files into one xacro file.
   - **initial_positions.yaml** - Used by `ASTRA_Arm.ros2_control.xacro` for mock hardware
   - **joint_limits** - Velocity and acceleration limits for each joint, required by Moveit2's motion planner
   - **kinematics.yaml** - Tells Moveit2 what IK solver to use
   - **moveit_controllers** - Tells Moveit2 what controllers are being used
   - **moveit.rviz** - rviz2 config used by `demo.launch.py`
   - **pilz_cartesian_limits.yaml** - Limits for the motion planner (idfk man :sob:)
   - **ros2_controllers.yaml** - Tells the controller manager how to spawn and configure the required ros2 controllers
 - `launch/`
   - **demo.launch.py** - Launches everything for Moveit2 using the other launch files in the same folder, including static_transform_publisher, robot_state_publisher, rviz2, Moveit2 core binaries, moveit_servo, ros2_control, and ros2_joy
   - **spawn_controllers.launch.py** - Launches all ros2 controllers for Moveit2

## Maintainer(s)

| Name | Email | Discord |
| ---- | ----- | ------- |
| David Sharpe | ds0196@uah.edu | ddavdd |
