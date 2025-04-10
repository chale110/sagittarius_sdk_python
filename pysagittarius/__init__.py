import os
import sys
import importlib.util

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# 查找 .so 文件
so_file = None
for root, dirs, files in os.walk(current_dir):
    for file in files:
        if file.endswith('.so') and file.startswith('pysagittarius'):
            so_file = os.path.join(root, file)
            print(f"Found .so file: {so_file}")
            break
    if so_file:
        break

if not so_file:
    # 向上一级目录查找
    parent_dir = os.path.dirname(current_dir)
    for root, dirs, files in os.walk(parent_dir):
        for file in files:
            if file.endswith('.so') and file.startswith('pysagittarius'):
                so_file = os.path.join(root, file)
                print(f"Found .so file in parent directory: {so_file}")
                break
        if so_file:
            break

if so_file:
    # 尝试直接从文件加载模块
    spec = importlib.util.spec_from_file_location("pysagittarius", so_file)
    pysagittarius = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pysagittarius)
    
    # 将所有内容导入到当前命名空间
    for name in dir(pysagittarius):
        if not name.startswith('_'):
            globals()[name] = getattr(pysagittarius, name)
    
    print(f"Successfully loaded module from {so_file}")
    print(f"Available attributes: {[name for name in dir(pysagittarius) if not name.startswith('_')]}")
else:
    print("Could not find pysagittarius.so file")
    # 尝试常规导入
    try:
        from pysagittarius import *
        print("Imported using standard import")
    except ImportError as e:
        print(f"Import error: {e}")
        try:
            from .pysagittarius import *
            print("Imported using relative import")
        except ImportError as e:
            print(f"Relative import error: {e}")

__version__ = "0.1.0"

def log_set_level(level):
    """临时的 log_set_level 实现"""
    print(f"Warning: Using dummy log_set_level({level})")
    # 实际上什么也不做
    pass