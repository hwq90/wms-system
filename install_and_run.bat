@echo off
echo ========================================
echo   小龙虾Python图片处理安装脚本
echo ========================================

echo.
echo 步骤1：检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请从 https://www.python.org/downloads/ 下载安装
    echo 安装时务必勾选"Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

echo.
echo 步骤2：安装Pillow和numpy...
python -m pip install Pillow numpy

if errorlevel 1 (
    echo ❌ 依赖安装失败
    echo 尝试升级pip...
    python -m pip install --upgrade pip
    python -m pip install Pillow numpy
)

echo.
echo 步骤3：运行图片处理脚本...
echo 处理：将第二张图片的颜色匹配到第一张图片

python process_images.py --source "第二张图片.png" --target "第一张图片.png" --output "小龙虾处理结果.png"

if errorlevel 1 (
    echo.
    echo ❌ 脚本运行失败
    echo 尝试简单版本...
    python simple_test.py
)

echo.
echo ========================================
if exist "小龙虾处理结果.png" (
    echo ✅ 处理完成！结果已保存为：小龙虾处理结果.png
    echo 文件位置：C:\Users\Administrator\clawd\小龙虾处理结果.png
) else (
    echo ⚠️  处理可能未完成
    echo 请检查错误信息
)

echo.
pause