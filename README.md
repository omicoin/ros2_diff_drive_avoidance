# ROS 2 与 Gazebo 差速底盘反应式局部避障仿真 (C++)

## 📌 项目简介
本项目是一个从零搭建的机器人仿真闭环验证项目。基于 **ROS 2 (Lyrical) + Gazebo (Jetty)** 仿真环境，使用 **C++ (rclcpp)** 编写核心避障算法，模拟移动机器人在受限环境中的局部动态避障逻辑。

## 🛠️ 技术栈
- **中间件**: ROS 2
- **仿真引擎**: Gazebo
- **编程语言**: C++ (rclcpp), Python (Launch)
- **核心工具**: URDF/Xacro, ros_gz_bridge

## 🚀 核心功能
1. **机器人建模**: 使用 URDF/Xacro，定义差速轮、万向轮与激光雷达模型，并配置物理碰撞与惯性矩阵。
2. **系统统筹**: 编写 Python Launch 文件，实现模型动态解析、Gazebo 环境启动与 TF 树发布。
3. **跨框架通信**: 配置 `ros_gz_bridge`，打通 ROS 2 与 Gazebo 底层数据格式（Twist, LaserScan）。
4. **C++ 避障算法**: 
   - 提取雷达正前方 60° 扇区数据，计算最小安全距离。
   - 引入 **迟滞控制 (Hysteresis)**（利用静态变量记忆历史转向），解决狭窄环境下的高频抖动问题，实现平滑绕障。

## 📂 目录结构
- `src/my_bot_description/`: 包含 URDF 模型、Gazebo World 文件及 Launch 启动脚本。
- `src/my_bot_control/`: 包含 C++ 避障核心逻辑 (`obstacle_avoider.cpp`)。
- `check_lidar.py`: 用于排查雷达坐标系朝向的四向数据打印测试脚本。

## 🎮 如何运行
```bash
# 编译
colcon build
source install/setup.bash

# 启动 Gazebo 仿真
ros2 launch my_bot_description gazebo.launch.py

# 启动 C++ 避障节点
ros2 run my_bot_control obstacle_avoider
