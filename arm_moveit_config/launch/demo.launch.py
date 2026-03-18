from moveit_configs_utils import MoveItConfigsBuilder

# from moveit_configs_utils.launches import generate_demo_launch

import os

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

from srdfdom.srdf import SRDF

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
    # return generate_demo_launch(moveit_config)
    launch_package_path = moveit_config.package_path

    ld = LaunchDescription()
    ld.add_action(
        DeclareBooleanLaunchArg(
            "debug",
            default_value=False,
            description="By default, we are not in debug mode",
        )
    )
    ld.add_action(DeclareBooleanLaunchArg("use_rviz", default_value=True))
    ld.add_action(
        DeclareLaunchArgument(
            "hardware_mode",
            default_value="mock_components",
            description="Hardware mode: 'mock_components' for simulation, 'physical' for real hardware",
        )
    )
    # If there are virtual joints, broadcast static tf by including virtual_joints launch
    virtual_joints_launch = (
        launch_package_path / "launch/static_virtual_joint_tfs.launch.py"
    )

    if virtual_joints_launch.exists():
        ld.add_action(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(virtual_joints_launch)),
            )
        )

    # Given the published joint states, publish tf for the robot links
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/rsp.launch.py")
            ),
            launch_arguments=[("hardware_mode", LaunchConfiguration("hardware_mode"))],
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/move_group.launch.py")
            ),
        )
    )

    # Run Rviz and load the default config to see the state of the move_group node
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/moveit_rviz.launch.py")
            ),
            condition=IfCondition(LaunchConfiguration("use_rviz")),
        )
    )

    # Fake joint driver
    ld.add_action(
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[
                str(moveit_config.package_path / "config/ros2_controllers.yaml"),
            ],
            remappings=[
                ("/controller_manager/robot_description", "/robot_description"),
            ],
        )
    )

    ## SERVO

    # This sets the update rate and planning group name for the acceleration limiting filter.
    acceleration_filter_update_period = {"update_period": 0.01}
    planning_group_name = {"planning_group_name": "astra_arm"}

    # Get parameters for the Servo node
    servo_params = {
        "moveit_servo": ParameterBuilder("arm_moveit_config")
        .yaml("config/astra_arm_simulated_config.yaml")
        .to_dict()
    }
    # Launch a standalone Servo node.
    # As opposed to a node component, this may be necessary (for example) if Servo is running on a different PC
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

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(launch_package_path / "launch/spawn_controllers.launch.py")
            ),
            launch_arguments=[("hardware_mode", LaunchConfiguration("hardware_mode"))],
        )
    )

    return ld
