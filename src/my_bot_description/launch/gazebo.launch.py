import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    #找到包的绝对路径
    pkg_path = get_package_share_directory('my_bot_description')
    #智能路径拼接器
    xacro_file = os.path.join(pkg_path, 'urdf', 'my_bot.urdf.xacro')
    #doc是指向DOM那棵树的“内存地址标签”  
    #xacro.process_file:读取指定路径下的 Xacro 源文件，
    #在内存中将其解析成一棵 DOM 树，完成所有宏的展开和变量的计算，
    #最后返回这棵结构化的树对象。
    #打包成python对象
    doc = xacro.process_file(xacro_file)
    #内存模型转纯文本字符串，存放机器人的外观、碰撞、物理惯性、运动学拓扑结构等数据。
    robot_desc = doc.toxml()

    #生成世界
    
    world_file = os.path.join(pkg_path, 'worlds', 'empty.world')
    #引用并执行另一个launch文件
    #.items()生成包含元组的视图对象
    #launch_arguments 在内存里，就是一个装着元组的临时清单
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    #创建节点模板
    #包路径，可执行文件，参数:列表套字典，日志输入位置

    #robot_state_publisher解析 URDF 来发布静态 TF 树
    #发布：动静态tf树，/tf 和 /tf_static；完整的URDF纯文本字符串/robot_description
    #订阅：/joint_states，实时接收轮子、机械臂等关节的角度数据。
    #robot_description存储在内存参数服务器中的纯文本字符串，
    #use_sim_time，让节点去订阅 Gazebo 的 /clock 话题，用仿真时钟代替系统物理时钟。
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}],
        output='screen'
    )

    # 通过调用 Gazebo 的底层服务（Service），在物理引擎里创建一个实体（Entity）
    # robot_description话题来自于robot_state_publisher发布
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_bot', '-z', '0.2'],
        output='screen'
    )

    # 桥接 Gazebo 和 ROS 2 的话题（速度控制、雷达、里程计）
    # parameter_bridge通信协议转换器
    # arguments<话题名>@<ROS 2数据类型>转@<Gazebo数据类型>
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry'
        ],
        output='screen'
    )
 
    #运行节点
    #并发，事件驱动，异步机制。
    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        spawn_entity,
        bridge
    ])
