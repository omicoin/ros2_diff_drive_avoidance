import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math

class LidarChecker(Node):
    def __init__(self):
        super().__init__('lidar_checker')
        # 订阅雷达数据
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        print("雷达透视节点已启动，请观察终端输出的四个方向距离...")

    def scan_callback(self, msg):
        size = len(msg.ranges)
        if size == 0:
            return

        # 计算四个方向的索引
        idx_front = 0                   # 0度 (正前)
        idx_left = size // 4            # 90度 (左侧)
        idx_back = size // 2            # 180度 (正后)
        idx_right = (size * 3) // 4     # 270度 (右侧)

        # 获取距离值 (如果超过最大量程或没扫到，可能是 inf)
        d_front = msg.ranges[idx_front]
        d_left = msg.ranges[idx_left]
        d_back = msg.ranges[idx_back]
        d_right = msg.ranges[idx_right]

        # 打印输出（保留两位小数）
        print(f"索引 0(0度): {d_front:.2f}m | 索引 {idx_left}(90度): {d_left:.2f}m | "
              f"索引 {idx_back}(180度): {d_back:.2f}m | 索引 {idx_right}(270度): {d_right:.2f}m")

def main(args=None):
    rclpy.init(args=args)
    node = LidarChecker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()