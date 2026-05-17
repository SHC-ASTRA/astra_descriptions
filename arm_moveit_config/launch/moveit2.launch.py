from moveit_configs_utils import MoveItConfigsBuilder

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg

from launch_param_builder import ParameterBuilder


def generate_launch_description():
    arm_moveit_config_share = FindPackageShare("arm_moveit_config").find(
        "arm_moveit_config"
    )

    moveit_config = MoveItConfigsBuilder(
        "ASTRA_Arm", package_name="arm_moveit_config"
    ).to_moveit_configs()

    assert moveit_config.package_path
    launch_package_path = Path(moveit_config.package_path)

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareBooleanLaunchArg(
            "debug",
            default_value=False,
            description="By default, we are not in debug mode",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            "hardware_mode",
            default_value="mock_components",
            description="Hardware mode: 'mock_components' for simulation, 'physical' for real hardware",
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            "robot_description_file",
            default_value=PathJoinSubstitution(
                [arm_moveit_config_share, "config", "ASTRA_Arm.urdf.xacro"]
            ),
            description="Path to the robot URDF/Xacro file. When integrated with rover, pass the combined rover_description.xacro",
        )
    )

    # Build robot_description from the specified file
    robot_description_config = ParameterValue(
        Command(
            [
                "xacro ",
                LaunchConfiguration("robot_description_file"),
                " hardware_mode:=",
                LaunchConfiguration("hardware_mode"),
            ]
        ),
        value_type=str,
    )

    ####################################################################################
    # Launch Nodes

    # RSP handled by rover_description launch

    # RViz handled by rover_description launch

    # Controllers handled by rover_description launch

    # Uses default values from moveit2 generated move_group.launch.py
    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": True,
        "capabilities": moveit_config.move_group_capabilities["capabilities"],
        "disable_capabilities": moveit_config.move_group_capabilities[
            "disable_capabilities"
        ],
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "monitor_dynamics": False,
    }

    # Moveit2 move group - Use move_group node directly with custom robot_description
    # (Cannot use auto-generated move_group.launch.py since it doesn't accept robot_description override)
    ld.add_action(
        Node(
            package="moveit_ros_move_group",
            executable="move_group",
            output="screen",
            parameters=[
                moveit_config.to_dict(),
                move_group_configuration,
                {"robot_description": robot_description_config},
            ],
        )
    )

    ####################################################################################
    # Moveit Servo

    # This sets the update rate and planning group name for the acceleration limiting filter.
    acceleration_filter_update_period = {"update_period": 0.01}
    planning_group_name = {"planning_group_name": "astra_arm"}

    # Get parameters for the Servo node
    servo_params = {
        "moveit_servo": ParameterBuilder("arm_moveit_config")
        .yaml("config/astra_arm_simulated_config.yaml")
        .to_dict()
    }

    # Moveit Servo node
    ld.add_action(
        Node(
            package="moveit_servo",
            executable="servo_node_main",
            parameters=[
                {"robot_description": robot_description_config},
                servo_params,
                moveit_config.robot_description_semantic,
                moveit_config.robot_description_kinematics,
            ],
            output="screen",
        )
    )

    return ld
