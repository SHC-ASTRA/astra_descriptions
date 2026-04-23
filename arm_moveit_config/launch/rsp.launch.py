from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ASTRA_Arm", package_name="arm_moveit_config"
    ).to_moveit_configs()
    ld = LaunchDescription()

    ld.add_action(
        DeclareLaunchArgument(
            "hardware_mode",
            default_value="mock_components",
            description="Hardware mode: 'mock_components' for simulation, 'physical' for real hardware",
        )
    )

    # Generate robot description with hardware_mode parameter
    robot_description_content = Command(
        [
            "xacro",
            " ",
            os.path.join(
                moveit_config.package_path,
                "config/ASTRA_Arm.urdf.xacro",
            ),
            " ",
            "hardware_mode:=",
            LaunchConfiguration("hardware_mode"),
        ]
    )

    # Publish robot description with hardware_mode parameter
    ld.add_action(
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": ParameterValue(
                        robot_description_content, value_type=str
                    )
                }
            ],
        )
    )

    return ld
