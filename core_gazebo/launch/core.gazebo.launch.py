#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_ros_gz_sim = FindPackageShare(package="ros_gz_sim").find("ros_gz_sim")
    pkg_share_gazebo = FindPackageShare(package="core_gazebo").find("core_gazebo")
    pkg_share_description = FindPackageShare(package="core_description").find(
        "core_description"
    )

    ld = LaunchDescription()

    gazebo_models_path = os.path.join(pkg_share_gazebo, "models")
    default_ros_gz_bridge_config_file_path = os.path.join(
        pkg_share_gazebo, "config/ros_gz_bridge.yaml"
    )

    ################################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="use_camera",
            default_value="false",
            description="Flag to enable the RGBD camera for Gazebo point cloud simulation",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="world_file",
            default_value="pick_and_place_demo.world",
            description="World file name (e.g., simple_demo.world, pick_and_place_demo.world)",
        )
    )

    ################################################################################################
    # Launch Nodes

    # Robot State Publisher and RViz
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [pkg_share_description, "launch", "display.launch.py"]
                )
            ),
            launch_arguments={("hardware_mode", "gazebo")},
        )
    )

    # ROS2 Controller Manager
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [pkg_share_description, "launch", "spawn_controllers.launch.py"]
                )
            ),
            launch_arguments={("hardware_mode", "gazebo")},
        )
    )

    # Set Gazebo model path - include both models directory and ROS packages
    ld.add_action(AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gazebo_models_path))

    # Add ROS packages path so Gazebo can resolve package:// URIs
    ld.add_action(
        AppendEnvironmentVariable(
            "GZ_SIM_RESOURCE_PATH", os.path.dirname(pkg_share_description)
        )
    )


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
            parameters=[{"config_file": default_ros_gz_bridge_config_file_path}],
            output="screen",
        )
    )

    # Bridge with optimizations to minimize latency and bandwidth when streaming image data
    ld.add_action(
        Node(
            package="ros_gz_image",
            executable="image_bridge",
            arguments=[
                "/camera_head/depth_image",
                "/camera_head/image",
            ],
            remappings=[
                ("/camera_head/depth_image", "/camera_head/depth/image_rect_raw"),
                ("/camera_head/image", "/camera_head/color/image_raw"),
            ],
            condition=IfCondition(LaunchConfiguration("use_camera")),
        )
    )


    # Spawn the robot in Gazebo
    gz_args = [
        ("-topic", "/robot_description"),
        ("-name", "core_rover"),
        ("-allow_renaming", "true"),
        ("-x", "0.0"),
        ("-y", "0.0"),
        ("-z", "0.75"),
        ("-R", "0.0"),
        ("-P", "0.0"),
        ("-Y", "0.0"),
    ]
    ld.add_action(
        Node(
            package="ros_gz_sim",
            executable="create",
            output="screen",
            arguments=sum(gz_args, ()),  # ROS2 requires flat list for shell args
        )
    )

    return ld
