from xmlrpc.client import boolean
from ament_index_python.packages import get_package_share_path
import launch
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_path = get_package_share_path("diffbot_navigation")
    model_path = package_path / "urdf/diffbot.urdf.xacro"
    rviz_config_path = package_path / "rviz/diffbot.rviz"
    world_path = package_path / "world/playground.sdf"
    ekf_config_path = package_path / "config/ekf.yaml"

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=str(model_path),
        description="Absolute path to robot urdf file",
    )
    sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        choices=["true", "false"],
        description="Flag to enable use simulation time",
    )
    rviz_arg = DeclareLaunchArgument(
        name="rvizconfig",
        default_value=str(rviz_config_path),
        description="Absolute path to rviz config file",
    )

    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]), value_type=str
    )
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "robot_description": robot_description,
            }
        ],
    )
    gazebo_process = ExecuteProcess(
        cmd=[
            "gazebo",
            "--verbose",
            "-s",
            "libgazebo_ros_init.so",
            "-s",
            "libgazebo_ros_factory.so",
            str(world_path),
        ],
        output="screen",
    )
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity",
            "demobot",
            "-topic",
            "robot_description",
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.0",
        ],
        output="screen",
    )

    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            str(ekf_config_path),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    return launch.LaunchDescription(
        [
            sim_time_arg,
            model_arg,
            rviz_arg,
            robot_state_publisher_node,
            gazebo_process,
            spawn_entity,
            robot_localization_node,
        ]
    )