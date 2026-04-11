#!/usr/bin/env python3
"""
Vercel 入口文件
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入 Flask app
from app import app

# 这是 Vercel 需要的入口
if __name__ == "__main__":
    app.run()