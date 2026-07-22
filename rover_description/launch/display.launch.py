# Visualize the URDF in RViz.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition

# https://docs.ros.org/en/rolling/p/launch/launch.substitutions.html
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    EqualsSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="rover_description").find("rover_description")

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="preview",
            description="Hardware mode: 'preview' for URDF preview, 'physical' for real hardware",
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
                ("hardware_mode", LaunchConfiguration("hardware_mode")),
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
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            # In preview mode, user should be able to change joint angles; otherwise,
            # they will be controlled by Gazebo or core_node from the state of the sim
            # or physical hardware.
            condition=IfCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "preview")
            ),
        )
    )

    return ld
