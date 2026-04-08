#!/usr/bin/env python3
"""
改进的图片处理脚本
"""

import os
from PIL import Image, ImageEnhance
import numpy as np

print("改进图片处理开始")
print("=" * 50)

# 图片路径
source_img = "第二张图片.png"
target_img = "第一张图片.png"
output_img = "改进处理结果.png"

print(f"源图片: {source_img}")
print(f"目标图片: {target_img}")
print(f"输出图片: {output_img}")
print()

try:
    # 加载图片
    print("1. 加载图片...")
    img_target = Image.open(target_img)
    img_source = Image.open(source_img)
    
    print(f"目标图片: {img_target.size}, {img_target.mode}")
    print(f"源图片: {img_source.size}, {img_source.mode}")
    
    # 调整尺寸
    print("2. 调整尺寸...")
    if img_target.size != img_source.size:
        print(f"从 {img_source.size} 调整到 {img_target.size}")
        img_source = img_source.resize(img_target.size, Image.Resampling.LANCZOS)
    
    # 转换为RGB
    if img_target.mode != 'RGB':
        img_target = img_target.convert('RGB')
    if img_source.mode != 'RGB':
        img_source = img_source.convert('RGB')
    
    # 转换为numpy数组
    target_arr = np.array(img_target).astype(np.float32)
    source_arr = np.array(img_source).astype(np.float32)
    
    # 方法1：直方图匹配（更精确）
    print("3. 进行直方图匹配...")
    
    # 对每个通道进行直方图匹配
    for channel in range(3):
        target_channel = target_arr[:, :, channel].flatten()
        source_channel = source_arr[:, :, channel].flatten()
        
        # 计算直方图
        target_hist, _ = np.histogram(target_channel, bins=256, range=(0, 255))
        source_hist, _ = np.histogram(source_channel, bins=256, range=(0, 255))
        
        # 计算累积分布函数
        target_cdf = target_hist.cumsum()
        target_cdf = target_cdf / target_cdf[-1]  # 归一化
        
        source_cdf = source_hist.cumsum()
        source_cdf = source_cdf / source_cdf[-1]  # 归一化
        
        # 创建映射表
        mapping = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            # 找到源CDF值最接近目标CDF值的索引
            idx = np.argmin(np.abs(source_cdf[i] - target_cdf))
            mapping[i] = idx
        
        # 应用映射
        source_arr[:, :, channel] = mapping[np.clip(source_arr[:, :, channel], 0, 255).astype(np.uint8)]
    
    # 方法2：亮度对比度调整
    print("4. 调整亮度对比度...")
    
    # 计算目标图片的亮度对比度
    target_mean = np.mean(target_arr)
    target_std = np.std(target_arr)
    source_mean = np.mean(source_arr)
    source_std = np.std(source_arr)
    
    # 调整亮度和对比度
    if source_std > 0:
        # 对比度调整
        source_arr = (source_arr - source_mean) * (target_std / source_std) + target_mean
    
    # 确保值在0-255范围内
    source_arr = np.clip(source_arr, 0, 255)
    
    # 创建结果图片
    result_img = Image.fromarray(source_arr.astype(np.uint8))
    
    # 保存结果
    print("5. 保存结果...")
    result_img.save(output_img)
    
    # 计算处理效果
    diff = np.abs(source_arr - target_arr)
    avg_diff = np.mean(diff)
    
    print("6. 处理效果评估:")
    print(f"平均像素差异: {avg_diff:.2f}/255")
    
    if avg_diff < 10:
        print("颜色匹配效果优秀")
    elif avg_diff < 20:
        print("颜色匹配效果良好")
    elif avg_diff < 30:
        print("颜色匹配效果一般")
    else:
        print("颜色匹配效果较差")
        print("建议: 可能需要手动调整或使用专业工具")
    
    print()
    print("处理完成!")
    print(f"结果文件: {output_img}")
    print(f"文件大小: {os.path.getsize(output_img)//1024:,} KB")
    print(f"位置: {os.path.abspath(output_img)}")
    
except Exception as e:
    print(f"处理失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 尝试简单方法
    try:
        print("\n尝试简单调整...")
        img_source = Image.open(source_img)
        img_target = Image.open(target_img)
        
        # 调整尺寸
        if img_source.size != img_target.size:
            img_source = img_source.resize(img_target.size)
        
        # 简单亮度调整
        enhancer = ImageEnhance.Brightness(img_source)
        img_source = enhancer.enhance(0.9)  # 稍微调暗
        
        img_source.save("简单调整结果.png")
        print("简单调整完成")
    except:
        print("所有方法都失败了")