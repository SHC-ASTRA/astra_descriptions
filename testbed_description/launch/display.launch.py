# Testbed Rover URDF Visualization

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    EqualsSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="testbed_description").find(
        "testbed_description"
    )

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="preview",
            description="Hardware mode: 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )

    ####################################################################################
    # Launch Nodes

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "nodes.launch.py"])
            ),
            launch_arguments={
                ("hardware_mode", "preview"),
                (
                    "spawn_rsp",
                    EqualsSubstitution(LaunchConfiguration("hardware_mode"), "preview"),
                ),
                ("spawn_controller_manager", "false"),
                ("spawn_controllers", "false"),
                ("spawn_rviz", "true"),
            },
        )
    )

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

    return ld
