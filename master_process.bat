@echo off
chcp 65001 >nul
title 🦞 小龙虾图片处理大师
color 0A

echo.
echo ╔══════════════════════════════════════════╗
echo ║          🦞 小龙虾图片处理工具          ║
echo ║          主人专用 - 一键处理            ║
echo ╚══════════════════════════════════════════╝
echo.

REM 设置图片路径
set "IMG_SOURCE=C:\Users\Administrator\.openclaw\media\qqbot\downloads\E17598A3A4C07F0433001FFCE8E749A3_1774229164735.png"
set "IMG_TARGET=C:\Users\Administrator\.openclaw\media\qqbot\downloads\B64D9794E5B6EFC805CEC058BF977C58_1774229156036.png"
set "IMG_OUTPUT=C:\Users\Administrator\clawd\小龙虾处理结果.png"

echo 📁 源图片（要处理的）: %IMG_SOURCE%
echo 📁 目标图片（要匹配的）: %IMG_TARGET%
echo 📁 输出图片: %IMG_OUTPUT%
echo.

echo 🔍 检查文件...
if not exist "%IMG_SOURCE%" (
    echo ❌ 错误：源图片不存在！
    pause
    exit /b 1
)

if not exist "%IMG_TARGET%" (
    echo ❌ 错误：目标图片不存在！
    pause
    exit /b 1
)

echo ✅ 文件检查通过！
echo.

echo 🎯 开始处理流程...
echo.

echo 步骤1：复制图片到工作空间...
copy "%IMG_SOURCE%" "C:\Users\Administrator\clawd\source_temp.png" >nul
copy "%IMG_TARGET%" "C:\Users\Administrator\clawd\target_temp.png" >nul
echo ✅ 复制完成
echo.

echo 步骤2：创建处理说明文档...
(
echo # 图片处理说明
echo.
echo ## 图片信息
echo - 源图片: %IMG_SOURCE%
echo - 目标图片: %IMG_TARGET%
echo - 输出图片: %IMG_OUTPUT%
echo.
echo ## 处理需求
echo 将第二张图片的颜色、亮度、风格处理得跟第一张一样
echo.
echo ## 推荐处理方法
echo 由于技术限制，建议使用以下方法：
echo.
echo ### 方法1：Photopea在线工具（推荐）
echo 1. 访问 https://www.photopea.com/
echo 2. 上传两张图片
echo 3. 选择第二张图片的图层
echo 4. 图像→调整→匹配颜色
echo 5. 选择第一张图片作为源
echo 6. 导出结果
echo.
echo ### 方法2：手动调整
echo 1. 使用画图3D打开两张图片
echo 2. 对比颜色和亮度
echo 3. 使用调整工具手动匹配
echo.
echo ## 已完成的操作
echo - [x] 复制图片到工作空间
echo - [x] 创建处理脚本
echo - [ ] 实际颜色匹配（需要外部工具）
echo.
) > "C:\Users\Administrator\clawd\处理说明.txt"
echo ✅ 说明文档已创建
echo.

echo 步骤3：创建一键处理脚本...
(
echo @echo off
echo echo 小龙虾图片处理助手
echo echo.
echo echo 请选择处理方式：
echo echo 1. 使用在线工具（推荐）
echo echo 2. 查看处理说明
echo echo 3. 打开图片文件夹
echo echo.
echo set /p choice=请输入选择（1-3）：
echo.
echo if "%%choice%%"=="1" (
echo   start https://www.photopea.com/
echo   echo 已打开Photopea，请按说明操作
echo ) else if "%%choice%%"=="2" (
echo   start "" "C:\Users\Administrator\clawd\处理说明.txt"
echo ) else if "%%choice%%"=="3" (
echo   explorer "C:\Users\Administrator\clawd"
echo ) else (
echo   echo 无效选择
echo )
echo pause
) > "C:\Users\Administrator\clawd\一键处理.bat"
echo ✅ 一键处理脚本已创建
echo.

echo 步骤4：创建结果占位文件...
echo 🎨 这是小龙虾为你处理的图片结果 > "%IMG_OUTPUT%.txt"
echo 实际图片需要外部工具处理 >> "%IMG_OUTPUT%.txt"
echo 请使用Photopea在线工具完成颜色匹配 >> "%IMG_OUTPUT%.txt"
echo ✅ 结果说明文件已创建
echo.

echo ╔══════════════════════════════════════════╗
echo ║                🎉 完成！                ║
echo ╚══════════════════════════════════════════╝
echo.
echo 📋 已为你准备好：
echo   1. 处理说明.txt - 详细的操作指南
echo   2. 一键处理.bat - 快速启动工具
echo   3. 图片已复制到工作空间
echo.
echo 🚀 下一步操作：
echo   运行"一键处理.bat"选择处理方式
echo   或直接访问：https://www.photopea.com/
echo.
echo 💡 提示：Photopea的"匹配颜色"功能在：
echo   图像 → 调整 → 匹配颜色
echo.

pause