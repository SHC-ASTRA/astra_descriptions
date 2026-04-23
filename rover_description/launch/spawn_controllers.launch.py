import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, EqualsSubstitution, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from srdfdom.srdf import SRDF


def generate_launch_description():
    ld = LaunchDescription()

    # Hardware Mode
    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="gazebo",
            description="Hardware mode: 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )

    # Controller Manager
    ld.add_action(
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[
                PathJoinSubstitution(
                    [
                        FindPackageShare("core_description"),
                        "config",
                        "ros2_controllers.yaml",
                    ]
                ),
                PathJoinSubstitution(
                    [
                        FindPackageShare("arm_moveit_config"),
                        "config",
                        "ros2_controllers.yaml",
                    ]
                ),
            ],
            remappings=[
                ("/controller_manager/robot_description", "/robot_description"),
            ],
            # Gazebo runs its own bullshit
            condition=UnlessCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "gazebo")
            ),
        )
    )

    # Controllers (Core)
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("core_description"),
                        "launch",
                        "spawn_controllers.launch.py",
                    ]
                )
            ),
            launch_arguments={("hardware_mode", LaunchConfiguration("hardware_mode"))},
        )
    )

    # Controllers (Arm)
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("arm_moveit_config"),
                        "launch",
                        "spawn_controllers.launch.py",
                    ]
                )
            ),
            launch_arguments={("hardware_mode", LaunchConfiguration("hardware_mode"))},
        )
    )

    return ld
