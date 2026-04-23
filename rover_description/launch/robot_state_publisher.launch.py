# Robot state publisher launch file for core rover

import os
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, EqualsSubstitution, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="rover_description").find("rover_description")

    ld = LaunchDescription()

    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="gazebo",
            description="Hardware mode: 'gazebo' for simulation, 'physical' for real hardware",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="urdf_model",
            default_value=PathJoinSubstitution([pkg_share, "urdf", "rover_description.xacro"]),
            description="Absolute path to robot urdf file",
        )
    )

    # Launch Nodes

    # Robot State Publisher
    # Subscribe to the joint states of the robot, publish /robot_description and static transforms.
    ld.add_action(
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[
                {
                    "use_sim_time": ParameterValue(EqualsSubstitution(LaunchConfiguration("hardware_mode"), "gazebo")),
                    "robot_description": ParameterValue(
                        Command(
                            [
                                "xacro ",
                                LaunchConfiguration("urdf_model"),
                                " hardware_mode:=",
                                LaunchConfiguration("hardware_mode"),
                                " omit_gz_ros2_control:=true",
                            ]
                        ),
                        value_type=str,
                    ),
                }
            ],
            arguments=[LaunchConfiguration("urdf_model")],
        )
    )

    return ld
