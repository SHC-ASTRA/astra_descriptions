from moveit_configs_utils import MoveItConfigsBuilder

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument

from launch_ros.actions import Node


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "ASTRA_Arm", package_name="arm_moveit_config"
    ).to_moveit_configs()
    # return generate_spawn_controllers_launch(moveit_config)
    controller_names = moveit_config.trajectory_execution.get(
        "moveit_simple_controller_manager", {}
    ).get("controller_names", [])

    ld = LaunchDescription()

    # Declared for parity with the other spawn_controllers launches (other launches pass it in).
    # The arm's controllers are the same across gazebo and physical; the joint_state_broadcaster
    # is spawned once by core (Gazebo) or the arm node publishes /joint_states directly (physical).
    ld.add_action(
        DeclareLaunchArgument(
            "hardware_mode",
            default_value="preview",
            description="Hardware mode: 'gazebo' for simulation, 'physical' for real hardware",
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
