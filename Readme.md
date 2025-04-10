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


