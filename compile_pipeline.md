1. 安装pybind11

2.创建一个C++文件（例如python_bindings.cpp）来定义Python绑定
```
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // 用于自动转换STL容器
#include "your_sagittarius_sdk_headers.h"  // 您的SDK头文件

namespace py = pybind11;

PYBIND11_MODULE(sagittarius_sdk_py, m) {
    m.doc() = "Sagittarius SDK Python bindings";  // 模块文档字符串
    
    // 绑定类
    py::class_<YourClass>(m, "YourClass")
        .def(py::init<>())
        .def("your_method", &YourClass::your_method)
        .def_property("your_property", &YourClass::get_property, &YourClass::set_property)
        .def_readonly("readonly_property", &YourClass::readonly_property);
    
    // 绑定函数
    m.def("your_function", &your_function, "Function description");
    
    // 绑定枚举
    py::enum_<YourEnum>(m, "YourEnum")
        .value("VALUE1", YourEnum::VALUE1)
        .value("VALUE2", YourEnum::VALUE2)
        .export_values();
}
```
3. 配置CMakeLists.txt
```
cmake_minimum_required(VERSION 3.4)
project(sagittarius_sdk_py)

# 添加C++11支持
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找Python解释器和库
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# 添加pybind11
find_package(pybind11 REQUIRED)

# 添加您的SDK源文件
file(GLOB SDK_SOURCES "src/*.cpp")

# 创建Python模块
pybind11_add_module(sagittarius_sdk_py 
    ${SDK_SOURCES}
    python_bindings.cpp
)

# 链接您的库（如果需要）
target_link_libraries(sagittarius_sdk_py PRIVATE your_other_libs)

# 包含头文件目录
target_include_directories(sagittarius_sdk_py PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 设置输出目录（可选）
set_target_properties(sagittarius_sdk_py PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python
)
```

4. 构建模块
```
mkdir build
cd build
cmake ..
make
```

5. 使用Python模块
```
import sagittarius_sdk_py

# 使用您绑定的类和函数
obj = sagittarius_sdk_py.YourClass()
obj.your_method()
result = sagittarius_sdk_py.your_function()
```
6. 打包为Python包（可选）
如果您想将模块分发给其他用户，可以创建setup.py文件：
```
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import setuptools

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        # 这里实现CMake构建过程
        # ...

setup(
    name='sagittarius_sdk_py',
    version='0.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='Python bindings for Sagittarius SDK',
    long_description='',
    ext_modules=[CMakeExtension('sagittarius_sdk_py')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
```