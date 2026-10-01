# All of the main node actions for the package in one place, so they can be invoked by
# the display, physical, and gazebo launches.

# Core localization launch, using robot_localization's ekf_node and navsat_transform

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    LaunchConfiguration,
    EqualsSubstitution,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="core_description").find("core_description")

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="preview",
            description="Mainly for RSP. 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="urdf_model",
            default_value=PathJoinSubstitution(
                [pkg_share, "urdf", "core_description.xacro"]
            ),
            description="Absolute path to robot urdf file",
        )
    )

    ####################################################################################
    # Launch Nodes

    # Robot Localization EKF
    ld.add_action(
        Node(
            package="robot_localization",
            executable="ekf_node",
            name="ekf_local_node",
            output="screen",
            parameters=[
                PathJoinSubstitution([pkg_share, "config/ekf_local.yaml"]),
                {
                    "use_sim_time": ParameterValue(
                        EqualsSubstitution(
                            LaunchConfiguration("hardware_mode"), "gazebo"
                        )
                    ),
                },
            ],
            remappings=[
                ("odometry/filtered", "/odometry/local"),
            ],
        )
    )

    # NavSat Transform Node
    ld.add_action(
        Node(
            package="robot_localization",
            executable="navsat_transform_node",
            name="navsat_transform_node",
            output="screen",
            parameters=[
                PathJoinSubstitution([pkg_share, "config/navsat.yaml"]),
                {
                    "use_sim_time": ParameterValue(
                        EqualsSubstitution(
                            LaunchConfiguration("hardware_mode"), "gazebo"
                        )
                    ),
                },
            ],
            remappings=[
                ("imu", "/core/feedback/imu/data"),
                ("gps/fix", "/core/feedback/gps/fix"),
                ("odometry/filtered", "/odometry/global"),
            ],
        )
    )

    # Robot Localization EKF global
    ld.add_action(
        Node(
            package="robot_localization",
            executable="ekf_node",
            name="ekf_global_node",
            output="screen",
            parameters=[
                PathJoinSubstitution([pkg_share, "config/ekf_global.yaml"]),
                {
                    "use_sim_time": ParameterValue(
                        EqualsSubstitution(
                            LaunchConfiguration("hardware_mode"), "gazebo"
                        )
                    ),
                },
            ],
            remappings=[
                ("odometry/filtered", "/odometry/global"),
            ],
        )
    )

    return ld
