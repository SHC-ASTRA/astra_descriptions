#!/usr/bin/env python3

import os
from launch import Action, LaunchContext, LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# Model height at spawn (m). If any part of the model starts underground, Gazebo spends
# a very long time buffering before starting the physics simulation. This causes the
# controllers, who are waiting for information from Gazebo's controller manager, to
# timeout and fail to activate, resulting in a model that cannot be controlled and
# publishes no TF frames. This is stupid and has bit me too many times to count.
CORE_SPAWN_Z = 0.5
TESTBED_SPAWN_Z = 0.1


def generate_launch_description():
    pkg_ros_gz_sim = FindPackageShare(package="ros_gz_sim").find("ros_gz_sim")
    pkg_share_gazebo = FindPackageShare(package="core_gazebo").find("core_gazebo")

    ld = LaunchDescription()

    gazebo_models_path = PathJoinSubstitution([pkg_share_gazebo, "models"])
    ros_gz_bridge_config_file = PathJoinSubstitution(
        [pkg_share_gazebo, "config", "ros_gz_bridge.yaml"]
    )

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_rviz",
            default_value="true",
            description="Whether to spawn RViz for URDF and TF2 visualization.",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="use_camera",
            default_value="false",
            description="Flag to enable the RGB camera for Gazebo perception simulation",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="world_file",
            default_value="pick_and_place_demo.world",
            description="World file name (e.g., simple_demo.world, pick_and_place_demo.world)",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="testbed",
            default_value="false",
            description="Whether to launch testbed instead of Core.",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_z",
            default_value="",
            description="Model height at spawn (m). Defaults to the per-model default.",
        )
    )

    ####################################################################################
    # Launch Nodes

    # Set Gazebo model path - include both models directory and ROS packages
    ld.add_action(AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gazebo_models_path))

    # Stays ahead of Gazebo below: it appends to GZ_SIM_RESOURCE_PATH, which gz_sim
    # only reads at startup.
    ld.add_action(OpaqueFunction(function=select_description_package))

    # Gazebo
    world_path = PathJoinSubstitution(
        [pkg_share_gazebo, "worlds", LaunchConfiguration("world_file")]
    )
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
            ),
            launch_arguments=[
                ("gz_args", [" -r -v 3 --render-engine ogre2 ", world_path])
            ],
        )
    )

    # Bridge ROS topics and Gazebo messages for establishing communication
    ld.add_action(
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            parameters=[{"config_file": ros_gz_bridge_config_file}],
            output="screen",
        )
    )

    # Bridge with optimizations to minimize latency and bandwidth when streaming image data
    ld.add_action(
        Node(
            package="ros_gz_image",
            executable="image_bridge",
            arguments=[
                "/camera_head/image",
            ],
            remappings=[
                ("/camera_head/image", "/camera_head/color/image_raw"),
            ],
            condition=IfCondition(LaunchConfiguration("use_camera")),
        )
    )

    return ld


def select_description_package(context: LaunchContext) -> list[Action]:
    """Bring up the description package the `testbed` parameter picks, and let Gazebo resolve its meshes."""
    # Ran at launch time: the `testbed` parameter has no value while the launch description is
    # being built, and the share path is consumed as a plain string, not a substitution.
    use_testbed = IfCondition(LaunchConfiguration("testbed")).evaluate(context)
    description_pkg_name = "testbed_description" if use_testbed else "core_description"

    pkg_share_description = FindPackageShare(package=description_pkg_name).find(
        description_pkg_name
    )

    actions: list[Action] = []

    # Make Gazebo work
    actions.append(
        AppendEnvironmentVariable(
            "GZ_SIM_RESOURCE_PATH", os.path.dirname(pkg_share_description)
        )
    )

    # Bring up RSP, controllers, and RViz from the required description package
    # (Core or Testbed)
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [pkg_share_description, "launch", "nodes.launch.py"]
                )
            ),
            launch_arguments={
                ("hardware_mode", "gazebo"),
                ("spawn_rsp", "true"),
                ("spawn_controller_manager", "false"),
                ("spawn_controllers", "true"),
                ("spawn_rviz", LaunchConfiguration("spawn_rviz")),
            },
        )
    )

    # Determine the spawn height for the model
    spawn_z = LaunchConfiguration("spawn_z").perform(context)
    if not spawn_z:
        spawn_z = str(TESTBED_SPAWN_Z if use_testbed else CORE_SPAWN_Z)
    try:
        float(spawn_z)
    except ValueError:
        raise RuntimeError(f"spawn_z must be a number in meters, got '{spawn_z}'")

    # Spawn the robot in Gazebo
    gz_args = [
        ("-topic", "/robot_description"),
        ("-name", "core_rover"),
        ("-allow_renaming", "true"),
        ("-x", "0.0"),
        ("-y", "0.0"),
        ("-z", str(spawn_z)),
        ("-R", "0.0"),
        ("-P", "0.0"),
        ("-Y", "0.0"),
    ]
    actions.append(
        Node(
            package="ros_gz_sim",
            executable="create",
            output="screen",
            arguments=sum(gz_args, ()),  # ROS2 requires flat list for shell args
        )
    )

    return actions
