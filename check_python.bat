@echo off
echo ========================================
echo   Python安装检查工具
echo ========================================

echo.
echo 检查Python安装状态...

echo 1. 查找Python...
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python不在PATH中
    echo 请确保安装时勾选了"Add Python to PATH"
    echo 或需要重启命令行窗口
) else (
    echo ✅ Python已找到
    python --version
)

echo.
echo 2. 查找pip...
where pip >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pip不在PATH中
    python -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ pip未安装
    ) else (
        echo ✅ pip已安装（通过python -m pip访问）
    )
) else (
    echo ✅ pip已找到
    pip --version
)

echo.
echo 3. 检查Python路径...
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo Python路径: %%i
)

echo.
echo ========================================
echo 如果显示"Python不在PATH中"，请：
echo 1. 重新安装Python，确保勾选"Add Python to PATH"
echo 2. 或手动添加Python到PATH环境变量
echo 3. 重启命令行窗口
echo.
echo 安装完成后，运行：install_and_run.bat
echo.

pause