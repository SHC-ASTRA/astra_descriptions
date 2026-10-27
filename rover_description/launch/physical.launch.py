# Ran on the physical rover.

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

# https://docs.ros.org/en/rolling/p/launch/launch.substitutions.html
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="rover_description").find("rover_description")

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    # Can't think of any

    ####################################################################################
    # Launch Nodes

    # RSP, Controller Manager, Controllers
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

    # Moveit2
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [
                        FindPackageShare("arm_moveit_config").find("arm_moveit_config"),
                        "launch",
                        "moveit2.launch.py",
                    ]
                )
            ),
            launch_arguments=[
                ("hardware_mode", "physical"),
                # Pass the Core+Arm URDF to MoveIt2 so it doesn't freak the fuck out
                (
                    "robot_description_file",
                    PathJoinSubstitution(
                        [pkg_share, "urdf", "rover_description.xacro"]
                    ),
                ),
            ],
        )
    )

    return ld
