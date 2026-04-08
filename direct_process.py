#!/usr/bin/env python3
"""
直接图片处理脚本 - 包含所有代码
"""

import sys
import os
import subprocess

print("🦞 小龙虾图片处理开始！")
print("=" * 50)

# 尝试导入Pillow和numpy
try:
    from PIL import Image
    import numpy as np
    print("✅ Pillow和numpy已安装")
except ImportError:
    print("❌ 缺少依赖，尝试安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "numpy"])
        print("✅ 依赖安装成功")
        from PIL import Image
        import numpy as np
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        print("请手动运行: python -m pip install Pillow numpy")
        exit(1)

# 图片路径
source_img = "第二张图片.png"  # 要处理的图片
target_img = "第一张图片.png"  # 目标图片
output_img = "小龙虾处理结果.png"

print(f"📁 源图片: {source_img}")
print(f"📁 目标图片: {target_img}")
print(f"📁 输出图片: {output_img}")
print()

# 检查文件是否存在
if not os.path.exists(source_img):
    print(f"❌ 源图片不存在: {source_img}")
    exit(1)

if not os.path.exists(target_img):
    print(f"❌ 目标图片不存在: {target_img}")
    exit(1)

try:
    # 加载图片
    print("📷 加载图片...")
    img_target = Image.open(target_img)  # 第一张（目标）
    img_source = Image.open(source_img)  # 第二张（要处理的）
    
    print(f"第一张图片: {img_target.size}, {img_target.mode}")
    print(f"第二张图片: {img_source.size}, {img_source.mode}")
    
    # 确保尺寸一致
    if img_target.size != img_source.size:
        print(f"🔄 调整尺寸: {img_source.size} -> {img_target.size}")
        img_source = img_source.resize(img_target.size, Image.Resampling.LANCZOS)
    
    # 转换为RGB
    if img_target.mode != 'RGB':
        img_target = img_target.convert('RGB')
    if img_source.mode != 'RGB':
        img_source = img_source.convert('RGB')
    
    # 获取颜色统计
    print("📊 计算颜色统计...")
    target_array = np.array(img_target).astype(np.float32)
    source_array = np.array(img_source).astype(np.float32)
    
    # 计算均值和标准差
    target_mean = np.mean(target_array, axis=(0, 1))
    target_std = np.std(target_array, axis=(0, 1))
    source_mean = np.mean(source_array, axis=(0, 1))
    source_std = np.std(source_array, axis=(0, 1))
    
    print(f"目标图片 - 均值: {target_mean}, 标准差: {target_std}")
    print(f"源图片 - 均值: {source_mean}, 标准差: {source_std}")
    
    # 颜色匹配
    print("🎨 进行颜色匹配...")
    for channel in range(3):
        if source_std[channel] > 0 and target_std[channel] > 0:
            # 调整源图片匹配目标图片的颜色特征
            source_array[:, :, channel] = (source_array[:, :, channel] - source_mean[channel]) * (target_std[channel] / source_std[channel]) + target_mean[channel]
    
    # 确保值在0-255范围内
    source_array = np.clip(source_array, 0, 255)
    
    # 创建结果图片
    result_img = Image.fromarray(source_array.astype(np.uint8))
    
    # 保存结果
    print("💾 保存结果...")
    result_img.save(output_img)
    
    # 显示文件信息
    file_size = os.path.getsize(output_img)
    print(f"✅ 处理完成！")
    print(f"📁 结果文件: {output_img}")
    print(f"📏 文件大小: {file_size:,} 字节 ({file_size/1024:.1f} KB)")
    print(f"📍 位置: {os.path.abspath(output_img)}")
    
    print("\n🎉 恭喜！图片处理成功完成！")
    
except Exception as e:
    print(f"❌ 处理失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n🔧 建议：")
    print("1. 确保Python已正确安装")
    print("2. 手动运行: python -m pip install Pillow numpy")
    print("3. 或使用在线工具: https://www.photopea.com/")
    
    # 尝试简单处理
    try:
        print("\n🔄 尝试简单处理...")
        img_source = Image.open(source_img)
        img_target = Image.open(target_img)
        
        # 简单调整尺寸
        if img_source.size != img_target.size:
            img_source = img_source.resize(img_target.size)
        
        img_source.save("简单处理结果.png")
        print("✅ 简单处理完成，保存为: 简单处理结果.png")
    except:
        print("❌ 简单处理也失败了")