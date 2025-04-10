cmake_minimum_required(VERSION 3.10)
project(pysagittarius)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找 Python 库
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# 查找 pybind11
find_package(pybind11 REQUIRED)

# 查找 Boost 库
find_package(Boost REQUIRED COMPONENTS thread system)

# 添加 Sagittarius SDK 头文件路径
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/sagittarius_sdk
    ${Boost_INCLUDE_DIRS}
)

# 查找SDK库文件 - 在系统路径中查找
find_library(SDK_SAGITTARIUS_ARM_LIB
    NAMES sdk_sagittarius_arm sagittarius_sdk
)

# 如果找不到库文件，则报错
if(NOT SDK_SAGITTARIUS_ARM_LIB)
    message(FATAL_ERROR "SDK library not found in system paths. Please make sure libsagittarius_sdk.so is installed in /usr/lib or another system library path.")
endif()

message(STATUS "Found SDK library: ${SDK_SAGITTARIUS_ARM_LIB}")

# 添加源文件
pybind11_add_module(pysagittarius MODULE
    pysagittarius.cc
)

# 链接 Sagittarius SDK 库
target_link_libraries(pysagittarius PRIVATE
    ${SDK_SAGITTARIUS_ARM_LIB}
    ${Boost_LIBRARIES}
)

# 确保输出名称正确
set_target_properties(pysagittarius PROPERTIES
    PREFIX ""
    SUFFIX ".so"
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
) 