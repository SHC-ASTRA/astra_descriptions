# Core Rover URDF Visualization

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
    EqualsSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = FindPackageShare(package="testbed_description").find(
        "testbed_description"
    )

    ld = LaunchDescription()

    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="preview",
            description="Hardware mode: 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_rsp",
            default_value="false",
            description="Whether to spawn the robot state publisher node.",
        )
    )

    # Launch Nodes

    # Joint State Publisher GUI - publish and graphically modify joint states
    ld.add_action(
        Node(
            condition=IfCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "preview")
            ),
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        )
    )

    # Robot State Publisher - publish URDF over /robot_description and transforms.
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [pkg_share, "launch", "robot_state_publisher.launch.py"]
                )
            ),
            launch_arguments={("hardware_mode", LaunchConfiguration("hardware_mode"))},
            condition=IfCondition(LaunchConfiguration("spawn_rsp")),
        )
    )

    # RViz
    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", os.path.join(pkg_share, "config/display.rviz")],
        )
    )

    return ld
