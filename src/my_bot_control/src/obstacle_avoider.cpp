#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <algorithm>
#include <cmath>

class ObstacleAvoider : public rclcpp::Node {
public: 
    //标准2D雷达模型sensor_msgs::msg::LaserScan
    //bind函数适配器
    ObstacleAvoider() : Node("obstacle_avoider") {
        //create_subscription<消息类型>(话题名, QoS策略默认reliable, 回调函数)
        /*template <typename MessageT, typename CallbackT>
        auto rclcpp::Node::create_subscription(
        const std::string& topic_name, 
        size_t qos, 
        CallbackT&& callback
        );*/
        sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/scan", 10,[this](const sensor_msgs::msg::LaserScan::SharedPtr msg) {
        this->scan_callback(msg);} );
        pub_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
        RCLCPP_INFO(this->get_logger(), "避障节点已启动！");
    }

private:
        void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
        
        //空间刚体速度，线速度linear，角速度angular，
        /*linear.x：前进/后退。
        linear.y：左/右平移（差速车不用）。
        linear.z：上/下升降（无人机用）。
        angular.x：绕 X 轴翻滚（机器人侧翻）。
        angular.y：绕 Y 轴俯仰（机器人点头/抬头）。
        angular.z：绕 Z 轴偏航（机器人左转/右转）*/ 
        auto cmd = geometry_msgs::msg::Twist();
        int size = msg->ranges.size();
        if (size == 0) return;

        // ==========================================
        // 1. 获取正前方 60 度的最小距离 (0度为正前，横跨左右两边)
        // ==========================================
        float min_front = 10.0;
        
        // 扫描正前方左半边：索引 0 到 30
        for (int i = 0; i <= 30 && i < size; ++i) {
            if (msg->ranges[i] < min_front && msg->ranges[i] > 0.1) {
                min_front = msg->ranges[i];
            }
        }
        
        // 扫描正前方右半边：索引 330 到 359
        for (int i = 0; i <= 30 && i < size; ++i) {
            int left_idx = size - 1 - i;
            if (left_idx >= 0 && msg->ranges[left_idx] < min_front && msg->ranges[left_idx] > 0.1) {
                min_front = msg->ranges[left_idx];
            }
        }

        // ==========================================
        // 2. 如果正前方安全 (大于 0.8m)，直接直行
        // ==========================================
        if (min_front >= 0.8) {
            cmd.linear.x = 0.25;
            cmd.angular.z = 0.0;
            RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "前方安全，距离: %.2f 米", min_front);
            pub_->publish(cmd);
            return;
        }

        // ==========================================
        // 3. 遇到障碍物，找左边和右边哪边更宽
        // ==========================================
        float min_left = 10.0;
        float min_right = 10.0;
        
        // 车的左侧，对应索引 60 到 120
        for (int i = 60; i <= 120 && i < size; ++i) {
            if (msg->ranges[i] < min_left && msg->ranges[i] > 0.1) {
                min_left = msg->ranges[i];
            }
        }
        
        // 车的右侧，对应索引 240 到 300
        for (int i = 240; i <= 300 && i < size; ++i) {
            if (msg->ranges[i] < min_right && msg->ranges[i] > 0.1) {
                min_right = msg->ranges[i];
            }
        }

        // 处理无穷大 (inf) 的情况
        if (std::isinf(min_left)) min_left = 5.0;
        if (std::isinf(min_right)) min_right = 5.0;

        // ==========================================
        // 4. 决策：哪边宽，往哪边转 (加入转向记忆)
        // ==========================================
        static int turn_direction = 0; // 0:未决定, 1:左转, -1:右转
        
        cmd.linear.x = 0.15; 
        
        // 如果误差很小 (比如两边都在 1.4m 左右)，就保持上一次的转向
        if (std::abs(min_left - min_right) < 0.2) {
            if (turn_direction == 1) {
                cmd.angular.z = 0.5; // 继续左转
            } else if (turn_direction == -1) {
                cmd.angular.z = -0.5; // 继续右转
            } else {
                cmd.angular.z = 0.5; // 默认左转
            }
        } else if (min_left > min_right) {
            turn_direction = 1;
            cmd.angular.z = 0.5;
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "遇障！向左转。");
        } else {
            turn_direction = -1;
            cmd.angular.z = -0.5;
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "遇障！向右转。");
        }

        pub_->publish(cmd);
    }

    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ObstacleAvoider>());
    rclcpp::shutdown();
    return 0;
}