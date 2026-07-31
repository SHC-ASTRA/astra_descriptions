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
- [Troubleshooting](#troubleshooting)
  - [Log noise](#log-noise)
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
  # View a URDF in RViz (either interactively or passively with mode:=preview|live)
$ ros2 launch core_description display.launch.py
$ ros2 launch testbed_description display.launch.py
$ ros2 launch arm_description display.launch.py
$ ros2 launch rover_description display.launch.py

  # Simulate in Gazebo
$ ros2 launch core_gazebo core.gazebo.launch.py     # Core only with diff_drive_controller
$ ros2 launch rover_description gazebo.launch.py    # Full rover; Core + Arm

  # Bring up ros2_control for real hardware (interfaces with anchor over topic_based_ros2_control)
$ ros2 launch core_description physical.launch.py   # Core only with diff_drive_controller
$ ros2 launch rover_description physical.launch.py  # Full rover; normally launched via Anchor's rover.launch.py
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
- **rover_description** - Combines Core and Arm into the full rover; includes launch files for the Gazebo sim and real-hardware ros2_control bringup.
- **testbed_description** - Like `core_description`, but for Testbed instead of Clucky.

## Major To-Do Items

- Reduce STL file complexity
- Add proper textures to Core and Arm
- Convert Arm to fully Xacro

## Troubleshooting

- **`Switch controller timed out after 5.000000 seconds!`, then `Failed to activate controller`** - Gazebo is taking too long to start

Controller activation only happens inside `controller_manager::update()`, which runs on the sim clock, and Humble hardcodes the 5 s timeout — so fix the sim, not the timeout. Nearly always the model spawned underground and the solver is taking a long time to figure it out. Raise `spawn_z` past the model's lowest collision point:

```bash
$ ros2 launch core_gazebo core.gazebo.launch.py spawn_z:=1.0
```

If that isn't it, good luck.

- **`amdgpu: drmGetDevice2 failed.`** — no GPU in the container, so Mesa falls back to llvmpipe

`run_container.sh` passes `/dev/dri` through when the host has it; check `ls /dev/dri` in the container and on the host. NVIDIA-only machines also need the nvidia-container-toolkit. Software rendering still runs, but will be slower and possibly create a fisheyed viewport.

### Log noise

| Message | Why |
| ------- | --- |
| `libEGL warning: egl: failed to create dri2 screen` | Only a problem if you have a single GPU. |
| `amdgpu: os_same_file_description couldn't determine...` | Prints regardless of whether the GPU works. |
| `groups: cannot find name for group ID 984` | The host's `render`/`video` GIDs, passed in for `/dev/dri` access. Applied fine, just unnamed inside the container. |
| `kdl_parser: The root link base_link has an inertia specified` | KDL ignores root-link inertia when building TF. Gazebo still uses it. |
| `IMU sensor 'core_emb_imu_sensor' not found in hardware_info` | The IMU reaches ROS via `gz-sim-imu-system` and `ros_gz_bridge` on `/core/imu/data`, not ros2_control. |
| `Desired controller update period (0.02 s) is slower than the gazebo simulation period (0.001 s)` |  Controller `update_rate` is 50 Hz against a 1 ms Gazebo step. |

## Maintainer(s)

| Name | Email | Discord |
| ---- | ----- | ------- |
| David Sharpe | ds0196@uah.edu | ddavdd |