import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. 找到包路径
    pkg_path = get_package_share_directory('my_bot_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'my_bot.urdf.xacro')

    # 2. 用代码自动解析 xacro，这样就不会有语法报错了
    doc = xacro.process_file(xacro_file)
    robot_desc = doc.toxml()

    # 3. 启动 robot_state_publisher 节点
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )

    # 4. 启动 RViz2 并读取配置（这里我们先让它启动默认界面）
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node
    ])
