import sys
import os
import importlib.util
import numpy as np
import time
import pygame

# 初始化pygame和手柄
pygame.init()
pygame.joystick.init()

# 检查是否有手柄连接
if pygame.joystick.get_count() == 0:
    print("错误：未检测到手柄，请连接XBOX手柄后重试")
    sys.exit(1)

# 获取第一个手柄
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"检测到手柄：{joystick.get_name()}")

# 加载Sagittarius机械臂库
so_file_path = os.path.abspath("./pysagittarius.so")

# 检查文件是否存在
if not os.path.exists(so_file_path):
    print(f"错误：找不到 .so 文件：{so_file_path}")
    sys.exit(1)

print(f"正在加载 .so 文件：{so_file_path}")

# 从文件加载模块
spec = importlib.util.spec_from_file_location("pysagittarius", so_file_path)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)

# 设置日志级别
ps.log_set_level(3)

# 连接机械臂
arm = ps.SagittariusArmReal("/dev/ttyACM0", 1000000, 500, 5)

# 初始化机械臂 IK 运算器
kinematics = ps.SagittariusArmKinematics(0, 0, 0)

# 设置销毁对象时不释放舵机
arm.SetFreeAfterDestructor(False)

print("Sagittarius机械臂已连接")

# 定义初始位置
INITIAL_POSITION = [0.3, 0, 0.3, 0, 0, 0]  # x, y, z, roll, pitch, yaw
GRIPPER_OPEN = 0.0
GRIPPER_CLOSE = -0.068
STEP_SIZE = 0.01  # 每次移动的步长
DEADZONE = 0.15   # 摇杆死区，小于这个值的输入将被忽略

# 移动到初始位置
def move_to_initial_position():
    success, joint_angles = kinematics.getIKinThetaEuler(*INITIAL_POSITION)
    if success:
        arm.SetAllServoRadian(joint_angles)
        print("已移动到初始位置")
    else:
        print("无法计算初始位置的逆运动学")

# 移动到指定位置
def move_to_position(x, y, z, roll, pitch, yaw):
    success, joint_angles = kinematics.getIKinThetaEuler(x, y, z, roll, pitch, yaw)
    if success:
        arm.SetAllServoRadian(joint_angles)
        return True
    else:
        print("无法计算逆运动学")
        return False

# 控制夹爪
def set_gripper(position):
    arm.arm_set_gripper_linear_position(position)

# 初始化机械臂位置
move_to_initial_position()
current_position = INITIAL_POSITION.copy()
gripper_position = GRIPPER_OPEN

# 按键映射
BUTTON_A = 0  # A按钮 - 夹爪关闭
BUTTON_B = 1  # B按钮 - 夹爪打开
BUTTON_Y = 3  # Y按钮 - 回到初始位置

# 方向键映射
AXIS_LEFT_X = 0   # 左摇杆X轴 - 控制Y轴移动
AXIS_LEFT_Y = 1   # 左摇杆Y轴 - 控制X轴移动
AXIS_RIGHT_X = 3  # 右摇杆X轴 - 控制偏航角(yaw)
AXIS_RIGHT_Y = 4  # 右摇杆Y轴 - 控制Z轴移动

# 主循环
running = True
print("控制说明：")
print("- 左摇杆：控制X和Y轴移动")
print("- 右摇杆：控制Z轴移动和偏航角")
print("- A按钮：关闭夹爪")
print("- B按钮：打开夹爪")
print("- Y按钮：回到初始位置")

try:
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 按钮按下事件
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_A:  # A按钮 - 关闭夹爪
                    gripper_position = GRIPPER_CLOSE
                    set_gripper(gripper_position)
                    print("夹爪关闭")
                
                elif event.button == BUTTON_B:  # B按钮 - 打开夹爪
                    gripper_position = GRIPPER_OPEN
                    set_gripper(gripper_position)
                    print("夹爪打开")
                
                elif event.button == BUTTON_Y:  # Y按钮 - 回到初始位置
                    move_to_initial_position()
                    current_position = INITIAL_POSITION.copy()
                    print("已回到初始位置")
        
        # 获取摇杆值并应用死区
        left_y = joystick.get_axis(AXIS_LEFT_Y)
        left_x = joystick.get_axis(AXIS_LEFT_X)
        right_y = joystick.get_axis(AXIS_RIGHT_Y)
        right_x = joystick.get_axis(AXIS_RIGHT_X)
        
        # 应用死区 - 如果摇杆值小于死区阈值，则视为零
        x_change = -left_y * STEP_SIZE if abs(left_y) > DEADZONE else 0
        y_change = left_x * STEP_SIZE if abs(left_x) > DEADZONE else 0
        z_change = -right_y * STEP_SIZE if abs(right_y) > DEADZONE else 0
        yaw_change = right_x * 2 if abs(right_x) > DEADZONE else 0
        
        # 如果有变化，更新位置
        if x_change != 0 or y_change != 0 or z_change != 0 or yaw_change != 0:
            new_position = current_position.copy()
            new_position[0] += x_change  # X轴
            new_position[1] += y_change  # Y轴
            new_position[2] += z_change  # Z轴
            new_position[5] += yaw_change  # 偏航角
            
            # 确保位置在合理范围内
            new_position[0] = max(0.1, min(0.4, new_position[0]))  # X轴限制
            new_position[1] = max(-0.3, min(0.3, new_position[1]))  # Y轴限制
            new_position[2] = max(0.05, min(0.4, new_position[2]))  # Z轴限制
            new_position[5] = max(-90, min(90, new_position[5]))  # 偏航角限制
            
            # 尝试移动到新位置
            if move_to_position(*new_position):
                current_position = new_position
                print(f"当前位置: X={current_position[0]:.3f}, Y={current_position[1]:.3f}, Z={current_position[2]:.3f}, Yaw={current_position[5]:.1f}")
        
        # 控制帧率
        time.sleep(0.05)

except KeyboardInterrupt:
    print("程序已中断")
finally:
    # 清理资源
    pygame.quit()
    print("程序结束")
