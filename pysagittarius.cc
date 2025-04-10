#include "pybind11/numpy.h"
#include "pybind11/pybind11.h"
#include "pybind11/eigen.h"
#include "pybind11/stl.h"
#include "sagittarius_sdk/sdk_sagittarius_arm/sdk_sagittarius_arm_real.h"
#include "sagittarius_sdk/sdk_sagittarius_arm/sdk_sagittarius_arm_log.h"

namespace py = pybind11;

PYBIND11_MODULE(pysagittarius, m) {
    m.doc() = "Python bindings for Sagittarius Arm SDK";

    // 设置日志级别函数
    m.def("log_set_level", &log_set_level, "Set log level (0-5)");
    
    // 绑定 ServoStruct 结构体
    py::class_<ServoStruct>(m, "ServoStruct")
        .def(py::init<>())
        .def_readwrite("id", &ServoStruct::id)
        .def_readwrite("value", &ServoStruct::value);

    // 绑定 SagittariusArmReal 类
    py::class_<sdk_sagittarius_arm::SagittariusArmReal>(m, "SagittariusArmReal")
        .def(py::init<std::string, int, int, int>(),
             py::arg("strSerialName") = "/dev/sagittarius",
             py::arg("Baudrate") = 1000000,
             py::arg("vel") = 500,
             py::arg("acc") = 5)
        .def("SetFreeAfterDestructor", &sdk_sagittarius_arm::SagittariusArmReal::SetFreeAfterDestructor,
             "Set whether to free servos after destructor")
        .def("CheckUpperLower", [](sdk_sagittarius_arm::SagittariusArmReal &self, py::array_t<float> js) {
            auto r = js.unchecked<1>();
            if (r.shape(0) < 6) {
                throw std::runtime_error("Input array must have at least 6 elements");
            }
            float js_arr[6];
            for (int i = 0; i < 6; i++) {
                js_arr[i] = r(i);
            }
            return self.CheckUpperLower(js_arr);
        })
        .def("CheckUpperLowerWithIndex", [](sdk_sagittarius_arm::SagittariusArmReal &self, py::list sv_list, int num) {
            if (num > 6) {
                throw std::runtime_error("Number of servos cannot exceed 6");
            }
            ServoStruct sv[6];
            for (int i = 0; i < num; i++) {
                py::object item = sv_list[i];
                sv[i].id = item.attr("id").cast<unsigned char>();
                sv[i].value = item.attr("value").cast<float>();
            }
            return self.CheckUpperLowerWithIndex(sv, num);
        })
        .def("arm_set_gripper_linear_position", &sdk_sagittarius_arm::SagittariusArmReal::arm_set_gripper_linear_position,
             "Set gripper linear position (-0.068~0.0)")
        .def("SetAllServoRadian", [](sdk_sagittarius_arm::SagittariusArmReal &self, py::array_t<float> joint_positions) {
            auto r = joint_positions.unchecked<1>();
            if (r.shape(0) < 6) {
                throw std::runtime_error("Input array must have at least 6 elements");
            }
            float js_arr[6];
            for (int i = 0; i < 6; i++) {
                js_arr[i] = r(i);
            }
            self.SetAllServoRadian(js_arr);
        })
        .def("GetCurrentJointStatus", [](sdk_sagittarius_arm::SagittariusArmReal &self) {
            float js[7];
            bool success = self.GetCurrentJointStatus(js);
            py::array_t<float> result(7);
            auto r = result.mutable_unchecked<1>();
            for (int i = 0; i < 7; i++) {
                r(i) = js[i];
            }
            return py::make_tuple(success, result);
        })
        .def("SetServoRadianWithIndex", [](sdk_sagittarius_arm::SagittariusArmReal &self, py::list sv_list, int num) {
            if (num > 6) {
                throw std::runtime_error("Number of servos cannot exceed 6");
            }
            ServoStruct sv[6];
            for (int i = 0; i < num; i++) {
                py::object item = sv_list[i];
                sv[i].id = item.attr("id").cast<unsigned char>();
                sv[i].value = item.attr("value").cast<float>();
            }
            self.SetServoRadianWithIndex(sv, num);
        })
        .def("ControlTorque", &sdk_sagittarius_arm::SagittariusArmReal::ControlTorque,
             "Control torque ('free' or 'lock')")
        .def("GetServoInfo", [](sdk_sagittarius_arm::SagittariusArmReal &self, unsigned char id, int timeout_ms) {
            int16_t info_arr[4];
            bool success = self.GetServoInfo(id, info_arr, timeout_ms);
            py::array_t<int16_t> result(4);
            auto r = result.mutable_unchecked<1>();
            for (int i = 0; i < 4; i++) {
                r(i) = info_arr[i];
            }
            return py::make_tuple(success, result);
        }, py::arg("id"), py::arg("timeout_ms") = 500)
        .def("SetServoAcceleration", &sdk_sagittarius_arm::SagittariusArmReal::SetServoAcceleration,
             "Set servo acceleration (0-254)")
        .def("SetServoVelocity", &sdk_sagittarius_arm::SagittariusArmReal::SetServoVelocity,
             "Set servo velocity (0-4096)")
        .def("SetServoTorque", [](sdk_sagittarius_arm::SagittariusArmReal &self, py::array_t<int> arm_torque) {
            auto r = arm_torque.unchecked<1>();
            if (r.shape(0) < 7) {
                throw std::runtime_error("Input array must have at least 7 elements");
            }
            int torque_arr[7];
            for (int i = 0; i < 7; i++) {
                torque_arr[i] = r(i);
            }
            return self.SetServoTorque(torque_arr);
        })
        .def_readonly("lower_joint_limits", &sdk_sagittarius_arm::SagittariusArmReal::lower_joint_limits)
        .def_readonly("upper_joint_limits", &sdk_sagittarius_arm::SagittariusArmReal::upper_joint_limits);

    // 绑定 SagittariusArmKinematics 类
    py::class_<sdk_sagittarius_arm::SagittariusArmKinematics>(m, "SagittariusArmKinematics")
        .def(py::init<float, float, float>(),
             py::arg("x") = 0.0f,
             py::arg("y") = 0.0f,
             py::arg("z") = 0.0f)
        .def("getIKinThetaMatrix", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, const Eigen::MatrixXd& M_EE, double eomg, double ev) {
            float theta_result[6];
            bool success = self.getIKinThetaMatrix(M_EE, theta_result, eomg, ev);
            py::array_t<float> result(6);
            auto r = result.mutable_unchecked<1>();
            for (int i = 0; i < 6; i++) {
                r(i) = theta_result[i];
            }
            return py::make_tuple(success, result);
        }, py::arg("M_EE"), py::arg("eomg") = 0.001, py::arg("ev") = 0.001)
        .def("getIKinThetaEuler", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, float x, float y, float z, float roll, float pitch, float yaw, double eomg, double ev) {
            float theta_result[6];
            bool success = self.getIKinThetaEuler(x, y, z, roll, pitch, yaw, theta_result, eomg, ev);
            py::array_t<float> result(6);
            auto r = result.mutable_unchecked<1>();
            for (int i = 0; i < 6; i++) {
                r(i) = theta_result[i];
            }
            return py::make_tuple(success, result);
        }, py::arg("x"), py::arg("y"), py::arg("z"), py::arg("roll"), py::arg("pitch"), py::arg("yaw"), py::arg("eomg") = 0.001, py::arg("ev") = 0.001)
        .def("getIKinThetaQuaternion", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, float x, float y, float z, float ox, float oy, float oz, float ow, double eomg, double ev) {
            float theta_result[6];
            bool success = self.getIKinThetaQuaternion(x, y, z, ox, oy, oz, ow, theta_result, eomg, ev);
            py::array_t<float> result(6);
            auto r = result.mutable_unchecked<1>();
            for (int i = 0; i < 6; i++) {
                r(i) = theta_result[i];
            }
            return py::make_tuple(success, result);
        }, py::arg("x"), py::arg("y"), py::arg("z"), py::arg("ox"), py::arg("oy"), py::arg("oz"), py::arg("ow"), py::arg("eomg") = 0.001, py::arg("ev") = 0.001)
        .def("getFKinMatrix", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, py::array_t<float> theta) {
            auto r = theta.unchecked<1>();
            if (r.shape(0) < 6) {
                throw std::runtime_error("Input array must have at least 6 elements");
            }
            float theta_arr[6];
            for (int i = 0; i < 6; i++) {
                theta_arr[i] = r(i);
            }
            Eigen::MatrixXd M_EE;
            bool success = self.getFKinMatrix(theta_arr, M_EE);
            return py::make_tuple(success, M_EE);
        })
        .def("getFKinEuler", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, py::array_t<float> theta) {
            auto r = theta.unchecked<1>();
            if (r.shape(0) < 6) {
                throw std::runtime_error("Input array must have at least 6 elements");
            }
            float theta_arr[6];
            for (int i = 0; i < 6; i++) {
                theta_arr[i] = r(i);
            }
            float xyz[3], euler[3];
            bool success = self.getFKinEuler(theta_arr, xyz, euler);
            py::array_t<float> xyz_result(3);
            py::array_t<float> euler_result(3);
            auto xyz_r = xyz_result.mutable_unchecked<1>();
            auto euler_r = euler_result.mutable_unchecked<1>();
            for (int i = 0; i < 3; i++) {
                xyz_r(i) = xyz[i];
                euler_r(i) = euler[i];
            }
            return py::make_tuple(success, xyz_result, euler_result);
        })
        .def("getFKinQuaternion", [](sdk_sagittarius_arm::SagittariusArmKinematics &self, py::array_t<float> theta) {
            auto r = theta.unchecked<1>();
            if (r.shape(0) < 6) {
                throw std::runtime_error("Input array must have at least 6 elements");
            }
            float theta_arr[6];
            for (int i = 0; i < 6; i++) {
                theta_arr[i] = r(i);
            }
            float xyz[3], quaternion[4];
            bool success = self.getFKinQuaternion(theta_arr, xyz, quaternion);
            py::array_t<float> xyz_result(3);
            py::array_t<float> quaternion_result(4);
            auto xyz_r = xyz_result.mutable_unchecked<1>();
            auto quaternion_r = quaternion_result.mutable_unchecked<1>();
            for (int i = 0; i < 3; i++) {
                xyz_r(i) = xyz[i];
            }
            for (int i = 0; i < 4; i++) {
                quaternion_r(i) = quaternion[i];
            }
            return py::make_tuple(success, xyz_result, quaternion_result);
        })
        .def_readonly("lower_joint_limits", &sdk_sagittarius_arm::SagittariusArmKinematics::lower_joint_limits)
        .def_readonly("upper_joint_limits", &sdk_sagittarius_arm::SagittariusArmKinematics::upper_joint_limits);
}
