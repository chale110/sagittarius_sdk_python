import sys
import os
import importlib.util
import numpy as np
import time

# 指定 .so 文件的路径（替换为你的实际路径）
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

print(f"可用的属性：{[name for name in dir(ps) if not name.startswith('_')]}")

# 设置日志级别
ps.log_set_level(3)

# 连接机械臂
arm = ps.SagittariusArmReal("/dev/ttyACM0", 1000000, 500, 5)

# 初始化机械臂 IK 运算器
kinematics = ps.SagittariusArmKinematics(0, 0, 0)

# 设置销毁对象时不释放舵机
arm.SetFreeAfterDestructor(False)

print("Sagittarius driver is running")

# 获取当前关节状态
success, js = arm.GetCurrentJointStatus()
print(f"Current joint status: {js}")

# 设置夹爪位置
arm.arm_set_gripper_linear_position(0.0)
time.sleep(1)

# 设置所有舵机的弧度
joint_positions = np.zeros(7)
joint_positions[5] = 1.576
arm.SetAllServoRadian(joint_positions)
time.sleep(1)

# 重置位置
joint_positions[5] = 0
arm.SetAllServoRadian(joint_positions)
time.sleep(1)

# 设置指定舵机的弧度
servo_list = []
for i in range(4):
    servo = ps.ServoStruct()
    servo.id = i + 1
    servo.value = 0.45 if i < 2 else (0.55 if i == 2 else 1.55)
    servo_list.append(servo)

arm.SetServoRadianWithIndex(servo_list, 4)
time.sleep(1)

# 设置夹爪关闭
arm.arm_set_gripper_linear_position(-0.068)
time.sleep(5)

# 获取舵机信息
success, info = arm.GetServoInfo(2, 200)
if success:
    print(f"Servo No.2 info: speed={info[0]}, payload={info[1]}%, voltage={info[2]}V, current={info[3]}mA")

# 使用逆运动学移动到目标位置
success, joint_angles = kinematics.getIKinThetaEuler(0.3, 0, 0.1, 0, 45, 0)
if success:
    arm.SetAllServoRadian(joint_angles)
    time.sleep(5)
    
    # 获取当前位置和姿态
    success, js = arm.GetCurrentJointStatus()
    success, xyz, euler = kinematics.getFKinEuler(js[:6])
    print(f"Current position: x={xyz[0]:.4f}, y={xyz[1]:.4f}, z={xyz[2]:.4f}")
    print(f"Current orientation: roll={euler[0]:.4f}, pitch={euler[1]:.4f}, yaw={euler[2]:.4f}")
    time.sleep(2)

# 使用四元数姿态
success, joint_angles = kinematics.getIKinThetaQuaternion(0.3, 0, 0.1, 0, 0.7068252, 0, 0.7073883)
if success:
    arm.SetAllServoRadian(joint_angles)
    time.sleep(5)

# 移动到其他位置
success, joint_angles = kinematics.getIKinThetaEuler(0.2, 0.2, 0.2, 0, 0, 45)
if success:
    arm.SetAllServoRadian(joint_angles)
    time.sleep(5)

success, joint_angles = kinematics.getIKinThetaEuler(0.3, 0, 0.3, 0, 0, 0)
if success:
    arm.SetAllServoRadian(joint_angles)
    time.sleep(5) 