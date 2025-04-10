from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess
import platform


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_call(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake必须安装才能构建扩展")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # 必要的CMake参数
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
            '-DPYTHON_EXECUTABLE=' + sys.executable
        ]

        # 配置参数
        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        # 多核编译
        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j4']

        # 创建build目录
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # 运行CMake命令
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

        # 复制.so文件到包目录
        if not os.path.exists(os.path.join(extdir, 'pysagittarius')):
            os.makedirs(os.path.join(extdir, 'pysagittarius'))
        
        # 确保__init__.py存在
        init_path = os.path.join(extdir, 'pysagittarius', '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write('from pysagittarius import *\n\n__version__ = "0.1.0"\n')


# 获取长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pysagittarius",
    version="0.1.0",
    description="Python绑定库用于控制Sagittarius机械臂",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chengleng Han",
    author_email="hanchengleng@whut.edu.cn",
    url="https://github.com/yourusername/pysagittarius",
    packages=find_packages(),
    ext_modules=[CMakeExtension('pysagittarius')],
    cmdclass=dict(build_ext=CMakeBuild),
    python_requires=">=3.6",
    install_requires=[
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    # 包含额外文件
    package_data={
        "": ["*.so", "*.md"],
    },
    include_package_data=True,
) 