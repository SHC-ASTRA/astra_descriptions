from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_spawn_controllers_launch

import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, EqualsSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from srdfdom.srdf import SRDF

from moveit_configs_utils.launch_utils import (
    add_debuggable_node,
    DeclareBooleanLaunchArg,
)


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ASTRA_Arm", package_name="arm_moveit_config"
    ).to_moveit_configs()
    # return generate_spawn_controllers_launch(moveit_config)
    controller_names = moveit_config.trajectory_execution.get(
        "moveit_simple_controller_manager", {}
    ).get("controller_names", [])

    ld = LaunchDescription()

    ld.add_action(
        DeclareLaunchArgument(
            "hardware_mode",
            default_value="mock_components",
            description="Hardware mode: 'mock_components' for simulation, 'physical' for real hardware",
        )
    )

    # Spawn joint_state_broadcaster only when using fake (non-Gazebo) hardware (mock_components)
    ld.add_action(
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster"],
            output="screen",
            condition=IfCondition(
                EqualsSubstitution(
                    LaunchConfiguration("hardware_mode"), "mock_components"
                )
            ),
        )
    )

    for controller in controller_names:
        ld.add_action(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[controller],
                output="screen",
            )
        )
    return ld
