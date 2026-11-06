cmake_minimum_required(VERSION 3.20)
project(my_bot_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 1. 告诉编译器，我们要生成一个叫 obstacle_avoider 的可执行文件，代码在 src/obstacle_avoider.cpp
add_executable(obstacle_avoider src/obstacle_avoider.cpp)

# 2. 链接依赖库，这样代码里才能 import rclcpp 等
#ament_target_dependencies(obstacle_avoider rclcpp sensor_msgs geometry_msgs)

# 2. 使用现代 CMake 语法链接依赖
# rclcpp::rclcpp 是 rclcpp 导出的现代 CMake Target
target_link_libraries(obstacle_avoider
  rclcpp::rclcpp
  ${sensor_msgs_TARGETS}
  ${geometry_msgs_TARGETS}
)

# 3. 安装这个可执行文件
install(TARGETS obstacle_avoider
  DESTINATION lib/${PROJECT_NAME})

ament_package()
