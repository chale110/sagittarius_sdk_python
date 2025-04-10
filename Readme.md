根据非ROS下的SDK：https://github.com/NXROBO/sagittarius_sdk 使用pybind11编译为可以在python环境直接调用的动态库文件


# 自动编译
根目录下：pip install -e .


# 手动编译
# 首先编译 pybind11

# pybind11包含 eigen3，只需要安装boost库


```
使用
```
# 删除 build 文件夹，重新编译

```bash
rm -rf build
mkdir build
cd build
cmake ..
make
```

# 编译后在build目录下生成pysagittarius.so文件

# 复制pysagittarius.so文件到当前目录
cp build/pysagittarius.so .

# 运行sagittarius_example.py
python sagittarius_example.py
```


