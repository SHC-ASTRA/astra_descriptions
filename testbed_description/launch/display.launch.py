# Visualize the Testbed URDF in RViz.
#
# One `mode` argument controls everything:
#   preview (default) - stand-alone URDF preview: local RSP + joint_state_publisher_gui
#                       (drag joint sliders) + RViz. Runs in its own ROS_DOMAIN_ID
#                       (preview_domain_id) so its fake /joint_states and /tf cannot
#                       interfere with the real rover.
#   live              - view a running rover/sim: RViz only, on the caller's domain,
#                       using the rover's /robot_description, /tf and /joint_states.
#                       Spawns no publishers, so it cannot interfere with the real rover.

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource

# https://docs.ros.org/en/rolling/p/launch/launch.substitutions.html
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    EqualsSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package="testbed_description").find(
        "testbed_description"
    )

    ld = LaunchDescription()

    ####################################################################################
    # Launch Arguments

    ld.add_action(
        DeclareLaunchArgument(
            name="mode",
            default_value="preview",
            description=(
                "'preview' for a sandboxed local URDF preview with slider joint control; "
                "'live' to view a running rover/sim (RViz only) on the current domain."
            ),
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            name="preview_domain_id",
            default_value="10",
            description=(
                "ROS_DOMAIN_ID used only in 'preview' mode to sandbox the preview from any "
                "live rover topics. Must differ from the rover's live ROS_DOMAIN_ID."
            ),
        )
    )

    is_preview = EqualsSubstitution(LaunchConfiguration("mode"), "preview")

    ####################################################################################
    # Domain isolation (preview only)

    # Sandbox the preview on its own DDS domain so its fake /joint_states and /tf can never
    # interfere with the live rover. Set before any node is launched so the nodes below inherit it.
    ld.add_action(
        SetEnvironmentVariable(
            name="ROS_DOMAIN_ID",
            value=LaunchConfiguration("preview_domain_id"),
            condition=IfCondition(is_preview),
        )
    )

    ####################################################################################
    # Launch Nodes

    # RSP (preview only) + RViz via the shared node launch. In 'live' mode we skip RSP: the
    # rover already publishes /robot_description and /tf, and a second RSP would be a duplicate
    # TF authority.
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([pkg_share, "launch", "nodes.launch.py"])
            ),
            launch_arguments={
                ("hardware_mode", "preview"),  # geometry only, no control
                ("spawn_rsp", is_preview),
                ("spawn_controller_manager", "false"),
                ("spawn_controllers", "false"),
                ("spawn_rviz", "true"),
            },
        )
    )

    # Joint State Publisher GUI - publish and graphically modify joint states in preview
    # mode. In 'live' mode the joint states come from the running rover/sim instead.
    ld.add_action(
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            condition=IfCondition(is_preview),
        )
    )

    return ld
