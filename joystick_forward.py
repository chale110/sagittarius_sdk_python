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

# 设置销毁对象时不释放舵机
arm.SetFreeAfterDestructor(False)

print("Sagittarius机械臂已连接")

# 定义初始位置（关节角度）
INITIAL_JOINT_POSITION = np.zeros(7)  # 7个关节的初始角度
GRIPPER_OPEN = 0.0
GRIPPER_CLOSE = -0.068
STEP_SIZE = 0.05  # 每次关节移动的步长（弧度）
DEADZONE = 0.15   # 摇杆死区

# 移动到初始位置
def move_to_initial_position():
    arm.SetAllServoRadian(INITIAL_JOINT_POSITION)
    print("已移动到初始位置")

# 设置单个舵机角度
def set_servo_angle(servo_id, angle):
    servo = ps.ServoStruct()
    servo.id = servo_id
    servo.value = angle
    arm.SetServoRadianWithIndex([servo], 1)

# 控制夹爪
def set_gripper(position):
    arm.arm_set_gripper_linear_position(position)

# 初始化机械臂位置
move_to_initial_position()
current_joint_angles = INITIAL_JOINT_POSITION.copy()
gripper_position = GRIPPER_OPEN

# 按键映射
BUTTON_Y = 3  # Y按钮 - 回到初始位置
BUTTON_A = 0  # A按钮 - 夹爪关闭
BUTTON_B = 1  # B按钮 - 夹爪打开

# 添加十字键映射
BUTTON_DPAD_UP = 0     # 十字键上 - 末端向前
BUTTON_DPAD_DOWN = 1   # 十字键下 - 末端向后
BUTTON_DPAD_LEFT = 2   # 十字键左 - 末端向左
BUTTON_DPAD_RIGHT = 3  # 十字键右 - 末端向右
HAT_DPAD = 0           # 十字键的HAT索引

# 摇杆和按钮映射到关节
# 左摇杆上下 - 关节1
# 左摇杆左右 - 关节2
# 右摇杆上下 - 关节3
# 右摇杆左右 - 关节4
# 左肩键 - 关节5
# 右肩键 - 关节6
# 左扳机 - 关节7 (负方向)
# 右扳机 - 关节7 (正方向)

AXIS_LEFT_Y = 1    # 左摇杆上下 - 关节1
AXIS_LEFT_X = 0    # 左摇杆左右 - 关节2
AXIS_RIGHT_Y = 4   # 右摇杆上下 - 关节3
AXIS_RIGHT_X = 3   # 右摇杆左右 - 关节4
BUTTON_LB = 4      # 左肩键 - 关节5 (负方向)
BUTTON_RB = 5      # 右肩键 - 关节5 (正方向)
BUTTON_BACK = 6    # 后退键 - 关节6 (负方向)
BUTTON_START = 7   # 开始键 - 关节6 (正方向)
AXIS_LT = 2        # 左扳机 - 关节7 (负方向)
AXIS_RT = 5        # 右扳机 - 关节7 (正方向)

# 关节限制（弧度）
JOINT_LIMITS = [
    (-2.0, 2.0),    # 关节1
    (-2.0, 2.0),    # 关节2
    (-2.0, 2.0),    # 关节3
    (-2.0, 2.0),    # 关节4
    (-2.0, 2.0),    # 关节5
    (-2.0, 2.0),    # 关节6
    (-2.0, 2.0)     # 关节7
]

# 主循环
running = True
print("控制说明：")
print("- 左摇杆上下：控制关节1")
print("- 左摇杆左右：控制关节2")
print("- 右摇杆上下：控制关节3")
print("- 右摇杆左右：控制关节4")
print("- 左肩键(LB)：控制关节5负方向")
print("- 右肩键(RB)：控制关节5正方向")
print("- 后退键(Back)：控制关节6负方向")
print("- 开始键(Start)：控制关节6正方向")
print("- 左扳机(LT)：控制关节7负方向")
print("- 右扳机(RT)：控制关节7正方向")
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
                    current_joint_angles = INITIAL_JOINT_POSITION.copy()
                    print("已回到初始位置")
        
        # 获取摇杆和按钮值
        joint_changes = np.zeros(7)
        
        # 关节1 - 左摇杆左右 (互换方向)
        left_x = joystick.get_axis(AXIS_LEFT_X)
        if abs(left_x) > DEADZONE:
            joint_changes[0] = left_x * STEP_SIZE  # 反转方向：去掉负号
        
        # 关节2 - 左摇杆上下 (互换方向)
        left_y = joystick.get_axis(AXIS_LEFT_Y)
        if abs(left_y) > DEADZONE:
            joint_changes[1] = -left_y * STEP_SIZE  # 反转方向：添加负号
        
        # 关节3 - 右摇杆上下 (保持不变)
        right_y = joystick.get_axis(AXIS_RIGHT_Y)
        if abs(right_y) > DEADZONE:
            joint_changes[2] = -right_y * STEP_SIZE
        
        # 关节4 - 右摇杆左右 (反向)
        right_x = joystick.get_axis(AXIS_RIGHT_X)
        if abs(right_x) > DEADZONE:
            joint_changes[3] = -right_x * STEP_SIZE  # 反向：添加负号
        
        # 关节5 - 左右肩键 (反向)
        if joystick.get_button(BUTTON_LB):
            joint_changes[4] = STEP_SIZE  # 反向：改为正值
        elif joystick.get_button(BUTTON_RB):
            joint_changes[4] = -STEP_SIZE  # 反向：改为负值
        
        # 关节6 - 后退和开始键 (反向)
        if joystick.get_button(BUTTON_BACK):
            joint_changes[5] = STEP_SIZE  # 反向：改为正值
        elif joystick.get_button(BUTTON_START):
            joint_changes[5] = -STEP_SIZE  # 反向：改为负值
        
        # 关节7 - 左右扳机 (反向)
        left_trigger = joystick.get_axis(AXIS_LT)
        right_trigger = joystick.get_axis(AXIS_RT)
        # 扳机键通常从-1开始，按下后变为1
        if left_trigger > -0.5:  # 左扳机按下
            joint_changes[6] = (left_trigger + 1) * STEP_SIZE / 2  # 反向：去掉负号
        elif right_trigger > -0.5:  # 右扳机按下
            joint_changes[6] = -(right_trigger + 1) * STEP_SIZE / 2  # 反向：添加负号
        
        # 获取十字键状态 - 控制末端位置
        hat = joystick.get_hat(HAT_DPAD)
        
        # 创建一个末端位置变化标志
        end_effector_changed = False
        end_effector_change = [0, 0, 0]  # [x, y, z]变化
        
        # 十字键上 - 末端向前 (X+)
        if hat[1] == 1:  # 上
            end_effector_change[0] = STEP_SIZE
            end_effector_changed = True
        # 十字键下 - 末端向后 (X-)
        elif hat[1] == -1:  # 下
            end_effector_change[0] = -STEP_SIZE
            end_effector_changed = True
        
        # 十字键右 - 末端向右 (Y-)
        if hat[0] == 1:  # 右
            end_effector_change[1] = -STEP_SIZE
            end_effector_changed = True
        # 十字键左 - 末端向左 (Y+)
        elif hat[0] == -1:  # 左
            end_effector_change[1] = STEP_SIZE
            end_effector_changed = True
        
        # 如果有末端位置变化，使用逆运动学计算关节角度
        if end_effector_changed:
            # 获取当前关节状态
            success, current_js = arm.GetCurrentJointStatus()
            if success:
                # 初始化运动学计算器
                kinematics = ps.SagittariusArmKinematics(0, 0, 0)
                
                # 计算当前末端位置
                success, xyz, euler = kinematics.getFKinEuler(current_js[:6])
                if success:
                    # 计算新的末端位置
                    new_xyz = [
                        xyz[0] + end_effector_change[0],
                        xyz[1] + end_effector_change[1],
                        xyz[2] + end_effector_change[2]
                    ]
                    
                    # 使用逆运动学计算新的关节角度
                    success, new_joint_angles = kinematics.getIKinThetaEuler(
                        new_xyz[0], new_xyz[1], new_xyz[2], 
                        euler[0], euler[1], euler[2]
                    )
                    
                    if success:
                        # 设置新的关节角度
                        arm.SetAllServoRadian(new_joint_angles)
                        # 更新当前关节角度
                        current_joint_angles = np.array(new_joint_angles)
                        print(f"末端位置: X={new_xyz[0]:.3f}, Y={new_xyz[1]:.3f}, Z={new_xyz[2]:.3f}")
                    else:
                        print("无法计算逆运动学，可能超出工作范围")
        
        # 如果有关节变化，更新位置
        elif np.any(joint_changes != 0):
            new_joint_angles = current_joint_angles.copy()
            
            # 更新关节角度
            for i in range(7):
                new_joint_angles[i] += joint_changes[i]
                # 确保在关节限制范围内
                new_joint_angles[i] = max(JOINT_LIMITS[i][0], min(JOINT_LIMITS[i][1], new_joint_angles[i]))
            
            # 设置新的关节角度
            arm.SetAllServoRadian(new_joint_angles)
            current_joint_angles = new_joint_angles
            
            # 打印当前关节角度
            print(f"当前关节角度: {', '.join([f'{angle:.2f}' for angle in current_joint_angles])}")
        
        # 控制帧率
        time.sleep(0.05)

except KeyboardInterrupt:
    print("程序已中断")
finally:
    # 清理资源
    pygame.quit()
    print("程序结束")
