# Ran on the physical rover.

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

# https://docs.ros.org/en/rolling/p/launch/launch.substitutions.html
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="core_description").find("core_description")

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
