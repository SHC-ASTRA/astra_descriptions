# All of the main node actions for the package in one place, so they can be invoked by
# the display, physical, and gazebo launches.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    EqualsSubstitution,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="rover_description").find("rover_description")

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    # Putting this table here bc it's the most centralized place for it.
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
            description="Mainly for RSP. 'preview' for URDF preview, 'gazebo' for simulation, 'physical' for real hardware",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_rsp",
            default_value="false",
            description="Whether to spawn the Robot State Publisher.",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_controller_manager",
            default_value="false",
            description="Whether to spawn the ros2_control controller manager.",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_controllers",
            default_value="false",
            description="Whether to spawn the ros2_control controllers.",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="spawn_rviz",
            default_value="false",
            description="Whether to spawn RViz for URDF and TF2 visualization.",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="urdf_model",
            default_value=PathJoinSubstitution(
                [pkg_share, "urdf", "rover_description.xacro"]
            ),
            description="Absolute path to robot urdf file",
        )
    )

    ####################################################################################
    # Launch Nodes

    # Robot State Publisher
    # Subscribe to the joint states of the robot, publish /robot_description and static transforms.
    ld.add_action(
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[
                {
                    "use_sim_time": ParameterValue(
                        EqualsSubstitution(
                            LaunchConfiguration("hardware_mode"), "gazebo"
                        )
                    ),
                    "robot_description": ParameterValue(
                        Command(
                            [
                                "xacro ",
                                LaunchConfiguration("urdf_model"),
                                " hardware_mode:=",
                                LaunchConfiguration("hardware_mode"),
                                " add_core_gz_ros2_control:=false",  # Core
                            ]
                        ),
                        value_type=str,
                    ),
                }
            ],
            arguments=[LaunchConfiguration("urdf_model")],
            condition=IfCondition(LaunchConfiguration("spawn_rsp")),
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
            # Should match the remaps in the <gazebo> block in rover_description.xacro
            remappings=[
                ("/controller_manager/robot_description", "/robot_description"),
                ("/diff_controller/cmd_vel_unstamped", "/core/control/cmd_vel"),
                ("/diff_controller/odom", "/core/feedback/wheel_odom"),
                ("/hand_controller/commands", "/arm/control/ik_gripper")
            ],
            # Gazebo runs its own bullshit
            condition=IfCondition(LaunchConfiguration("spawn_controller_manager")),
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
            condition=IfCondition(LaunchConfiguration("spawn_controllers")),
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
            condition=IfCondition(LaunchConfiguration("spawn_controllers")),
        )
    )

    # RViz
    ld.add_action(
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=[
                "-d",
                PathJoinSubstitution([pkg_share, "config", "display.rviz"]),
            ],
            # Basically everything that uses this launch file wants RViz unless you don't
            condition=IfCondition(LaunchConfiguration("spawn_rviz")),
        )
    )

    return ld
