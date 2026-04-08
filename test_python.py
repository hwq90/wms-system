#!/usr/bin/env python3
"""
测试Python环境并安装依赖
"""

import sys
import subprocess
import os

def check_and_install():
    print("🦞 检查Python环境...")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查Pillow
    try:
        from PIL import Image
        print("✅ Pillow已安装")
        return True
    except ImportError:
        print("❌ Pillow未安装")
        
        # 尝试安装
        print("🔄 尝试安装Pillow...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("✅ Pillow安装成功")
            return True
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False
    
    # 检查numpy
    try:
        import numpy as np
        print("✅ numpy已安装")
        return True
    except ImportError:
        print("❌ numpy未安装")
        
        # 尝试安装
        print("🔄 尝试安装numpy...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
            print("✅ numpy安装成功")
            return True
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False

def main():
    print("=" * 50)
    print("Python环境检查工具")
    print("=" * 50)
    
    success = check_and_install()
    
    if success:
        print("\n🎉 环境检查完成！")
        print("现在可以运行图片处理脚本了")
    else:
        print("\n❌ 环境检查失败")
        print("请手动安装依赖:")
        print("1. 确保Python已正确安装")
        print("2. 运行: python -m pip install Pillow numpy")
        print("3. 或从 https://www.python.org/downloads/ 重新安装Python")

if __name__ == "__main__":
    main()