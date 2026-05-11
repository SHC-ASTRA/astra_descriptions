# Main entrypoint for URDF stuff

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

    # -------------------------------------------------------------------------------- #
    # Launch Arguments

    # ===================================== #
    #             hardware_mode             #
    # ===================================== #
    #             JSP_GUI  RSP  RViz  ctrl  #
    #  Preview      X       X    X          #
    #  Gazebo               X    ?     X    #
    #  Physical                  X     X    #
    # ===================================== #
    ld.add_action(
        DeclareLaunchArgument(
            name="hardware_mode",
            default_value="preview",
            description="Hardware mode: 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )

    # Seems a little odd to be able to disable RViz in the 'display' launch file...
    # But I don't always need it when I am launching Gazebo. But by default, it should.
    # Refer to the table above for why the launch file is laid out this way.
    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_rviz",
            default_value="true",
            description="Whether to spawn RViz for URDF and TF2 visualization.",
        )
    )

    # -------------------------------------------------------------------------------- #
    # Regular Nodes

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

    # Robot State Publisher - publish URDF over /robot_description and transforms.
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution(
                    [pkg_share, "launch", "robot_state_publisher.launch.py"]
                )
            ),
            # hardware_mode is passed to Xacro as an argument to control whether
            # ros2_control should interface with Gazebo or topic_based_ros2_control.
            launch_arguments={("hardware_mode", LaunchConfiguration("hardware_mode"))},
            # Only spawn the robot state publisher if not running the rover physically;
            # RSP is necessary for 'preview' to correctly show the positions of each link
            # relative to eachother. Gazebo needs it because it reads from /robot_description
            # to spawn the robot. If you are running the rover physically, spawning the RSP
            # will be handled by `ros2 launch anchor_pkg rover.launch.py use_ros2_control:=true`
            # on the physical rover.
            condition=UnlessCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "physical")
            ),
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
            # Basically everything that uses this launch file wants RViz unless you don't
            condition=IfCondition(LaunchConfiguration("spawn_rviz")),
        )
    )

    # -------------------------------------------------------------------------------- #
    # ros2_control

    # Controller Manager
    ld.add_action(
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[
                PathJoinSubstitution(
                    [
                        FindPackageShare("rover_description"),
                        "config",
                        "ros2_controllers.yaml",
                    ]
                ),
            ],
            remappings=[
                ("/controller_manager/robot_description", "/robot_description"),
            ],
            # Gazebo runs its own bullshit, only needed if physical
            condition=IfCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "physical")
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
            condition=UnlessCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "preview")
            ),
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
            condition=UnlessCondition(
                EqualsSubstitution(LaunchConfiguration("hardware_mode"), "preview")
            ),
        )
    )

    return ld
