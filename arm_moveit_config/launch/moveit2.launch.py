from moveit_configs_utils import MoveItConfigsBuilder

from pathlib import Path

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from moveit_configs_utils.launch_utils import (
    add_debuggable_node,
    DeclareBooleanLaunchArg,
)

from launch_param_builder import ParameterBuilder
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ASTRA_Arm", package_name="arm_moveit_config"
    ).to_moveit_configs()

    assert moveit_config.package_path
    launch_package_path = Path(moveit_config.package_path)

    ld = LaunchDescription()

    # -------------------------------------------------------------------------------- #
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

    # -------------------------------------------------------------------------------- #
    # Regular Nodes

    # TODO: needed?
    # Broadcast static tf by including virtual_joints launch
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/static_virtual_joint_tfs.launch.py")
            ),
        )
    )

    # RSP handled by rover_description launch

    # TODO: wtf does this do
    # Moveit2 move group
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/move_group.launch.py")
            ),
        )
    )

    # RViz handled by rover_description launch

    # Controllers handled by rover_description launch

    # -------------------------------------------------------------------------------- #
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
                servo_params,
                moveit_config.robot_description,
                moveit_config.robot_description_semantic,
                moveit_config.robot_description_kinematics,
            ],
            output="screen",
        )
    )

    return ld
