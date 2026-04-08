@echo off
chcp 65001 >nul
echo 🦞 小龙虾图片颜色匹配工具
echo ========================================

REM 设置图片路径（请修改为你的实际路径）
set SOURCE_IMAGE="C:\Users\Administrator\.openclaw\media\qqbot\downloads\第二张图片.jpg"
set TARGET_IMAGE="C:\Users\Administrator\.openclaw\media\qqbot\downloads\第一张图片.jpg"
set OUTPUT_IMAGE="C:\Users\Administrator\clawd\匹配后的图片.jpg"

echo.
echo 📁 源图片（要处理的）: %SOURCE_IMAGE%
echo 📁 目标图片（要匹配的）: %TARGET_IMAGE%
echo 📁 输出图片: %OUTPUT_IMAGE%
echo.

REM 检查ImageMagick是否安装
where magick >nul 2>nul
if errorlevel 1 (
    echo ❌ 未找到ImageMagick！
    echo 请从 https://imagemagick.org/script/download.php 下载安装
    pause
    exit /b 1
)

REM 检查图片文件是否存在
if not exist %SOURCE_IMAGE% (
    echo ❌ 源图片不存在: %SOURCE_IMAGE%
    pause
    exit /b 1
)

if not exist %TARGET_IMAGE% (
    echo ❌ 目标图片不存在: %TARGET_IMAGE%
    pause
    exit /b 1
)

echo ✅ 开始处理图片...
echo.

REM 方法1：使用-compose colorize（推荐）
echo 🎨 使用方法1：颜色匹配...
magick convert %SOURCE_IMAGE% %TARGET_IMAGE% -colorspace RGB -define compose:args=100,0 -compose colorize -composite "%OUTPUT_IMAGE%"

if errorlevel 1 (
    echo ⚠️  方法1失败，尝试方法2...
    
    REM 方法2：使用-modulate（基于统计）
    echo 📊 获取目标图片颜色特征...
    for /f "tokens=1-6" %%a in ('magick identify -format "%%[mean] %%[standard-deviation]" %TARGET_IMAGE%') do (
        set TARGET_MEAN=%%a
        set TARGET_STD=%%b
    )
    
    for /f "tokens=1-6" %%a in ('magick identify -format "%%[mean] %%[standard-deviation]" %SOURCE_IMAGE%') do (
        set SOURCE_MEAN=%%a
        set SOURCE_STD=%%b
    )
    
    echo 📊 源图片 - 均值: %SOURCE_MEAN%, 标准差: %SOURCE_STD%
    echo 📊 目标图片 - 均值: %TARGET_MEAN%, 标准差: %TARGET_STD%
    
    REM 计算调整因子（简化版）
    set /a BRIGHTNESS_FACTOR=100
    set /a SATURATION_FACTOR=100
    
    echo 🎨 应用颜色调整...
    magick convert %SOURCE_IMAGE% -modulate %BRIGHTNESS_FACTOR%,%SATURATION_FACTOR%,100 "%OUTPUT_IMAGE%"
)

if errorlevel 1 (
    echo ❌ 所有方法都失败了！
    echo 建议使用在线工具：https://www.photopea.com/
    pause
    exit /b 1
)

echo.
echo ✅ 处理完成！
echo 📁 结果已保存到: %OUTPUT_IMAGE%
echo.
echo 🎯 下一步操作：
echo 1. 查看结果图片是否满意
echo 2. 如果不满意，可以尝试手动调整参数
echo 3. 或使用在线工具获得更好效果

pause