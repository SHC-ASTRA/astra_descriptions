# Ran on the physical rover.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition

# https://docs.ros.org/en/rolling/p/launch/launch.substitutions.html
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
    EqualsSubstitution,
    OrSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = FindPackageShare(package="rover_description").find("rover_description")

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    # Can't think of any

    ####################################################################################
    # Launch Nodes

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "nodes.launch.py"])
            ),
            launch_arguments={
                ("hardware_mode", "physical"),
                ("spawn_rsp", "true"),
                ("spawn_controller_manager", "true"),
                ("spawn_controllers", "true"),
                ("spawn_rviz", "false"),
            },
        )
    )

    return ld
