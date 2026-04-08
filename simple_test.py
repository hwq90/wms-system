#!/usr/bin/env python3
"""
简单图片处理测试
"""

import os
from PIL import Image

print("🦞 小龙虾简单图片处理测试")
print("=" * 40)

# 图片路径
source_img = "第二张图片.png"
target_img = "第一张图片.png"
output_img = "简单处理结果.png"

print(f"源图片: {source_img}")
print(f"目标图片: {target_img}")
print(f"输出图片: {output_img}")
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
    img1 = Image.open(target_img)  # 第一张（目标）
    img2 = Image.open(source_img)  # 第二张（要处理的）
    
    print(f"第一张图片: {img1.size}, {img1.mode}")
    print(f"第二张图片: {img2.size}, {img2.mode}")
    
    # 简单的处理：调整第二张图片匹配第一张的尺寸
    print("🔄 调整尺寸...")
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)
        print(f"尺寸已调整: {img2.size}")
    
    # 简单的颜色调整：匹配平均亮度
    print("🎨 简单颜色调整...")
    
    # 转换为RGB（如果图片有alpha通道）
    if img1.mode != 'RGB':
        img1 = img1.convert('RGB')
    if img2.mode != 'RGB':
        img2 = img2.convert('RGB')
    
    # 这里可以添加更复杂的颜色匹配算法
    # 目前只是简单的尺寸调整和格式转换
    
    # 保存结果
    print("💾 保存结果...")
    img2.save(output_img)
    
    print(f"✅ 处理完成！结果保存为: {output_img}")
    print(f"📏 文件大小: {os.path.getsize(output_img)} 字节")
    
except Exception as e:
    print(f"❌ 处理失败: {e}")
    import traceback
    traceback.print_exc()