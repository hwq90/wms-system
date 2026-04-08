#!/usr/bin/env python3
"""
图片处理工具 - 完整版
可以将第二张图片处理得跟第一张一样
"""

import os
import sys
import argparse
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

def load_image(image_path):
    """加载图片"""
    try:
        img = Image.open(image_path)
        print(f"✅ 成功加载图片: {os.path.basename(image_path)}")
        print(f"   格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
        return img
    except Exception as e:
        print(f"❌ 加载图片失败: {e}")
        return None

def save_image(image, output_path):
    """保存图片"""
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        print(f"✅ 图片已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 保存图片失败: {e}")
        return False

def get_image_stats(image):
    """获取图片的统计信息（均值、标准差）"""
    img_array = np.array(image)
    if len(img_array.shape) == 3:
        # RGB图片
        mean = np.mean(img_array, axis=(0, 1))
        std = np.std(img_array, axis=(0, 1))
    else:
        # 灰度图片
        mean = np.mean(img_array)
        std = np.std(img_array)
        mean = np.array([mean, mean, mean])
        std = np.array([std, std, std])
    
    return {'mean': mean, 'std': std}

def match_color(source_img, target_img):
    """
    将源图片的颜色匹配到目标图片
    让源图片的颜色风格变得跟目标图片一样
    """
    print("🎨 开始颜色匹配...")
    
    # 转换为RGB（如果图片有alpha通道）
    if source_img.mode != 'RGB':
        source_img = source_img.convert('RGB')
    if target_img.mode != 'RGB':
        target_img = target_img.convert('RGB')
    
    # 确保尺寸一致（如果不一致，调整源图片尺寸）
    if source_img.size != target_img.size:
        print(f"⚠️  尺寸不一致，调整源图片尺寸: {source_img.size} -> {target_img.size}")
        source_img = source_img.resize(target_img.size, Image.Resampling.LANCZOS)
    
    # 计算颜色统计
    source_stats = get_image_stats(source_img)
    target_stats = get_image_stats(target_img)
    
    print(f"📊 源图片统计 - 均值: {source_stats['mean']}, 标准差: {source_stats['std']}")
    print(f"📊 目标图片统计 - 均值: {target_stats['mean']}, 标准差: {target_stats['std']}")
    
    # 颜色匹配
    source_array = np.array(source_img).astype(np.float32)
    
    for channel in range(3):
        source_mean = source_stats['mean'][channel]
        source_std = source_stats['std'][channel]
        target_mean = target_stats['mean'][channel]
        target_std = target_stats['std'][channel]
        
        # 避免除零
        if source_std > 0 and target_std > 0:
            # 颜色匹配公式：调整源图片的统计特征匹配目标图片
            source_array[:, :, channel] = (source_array[:, :, channel] - source_mean) * (target_std / source_std) + target_mean
        else:
            print(f"⚠️  通道{channel}标准差为0，跳过颜色匹配")
    
    # 确保值在0-255范围内
    source_array = np.clip(source_array, 0, 255)
    
    result = Image.fromarray(source_array.astype(np.uint8))
    print("✅ 颜色匹配完成!")
    return result

def match_brightness_contrast(source_img, target_img):
    """匹配亮度和对比度"""
    print("🌞 匹配亮度和对比度...")
    
    # 转换为RGB（如果图片有alpha通道）
    if source_img.mode != 'RGB':
        source_img = source_img.convert('RGB')
    if target_img.mode != 'RGB':
        target_img = target_img.convert('RGB')
    
    # 计算亮度（转换为HSV的V通道）
    source_hsv = source_img.convert('HSV')
    target_hsv = target_img.convert('HSV')
    
    source_v = np.array(source_hsv.split()[2]).astype(np.float32)
    target_v = np.array(target_hsv.split()[2]).astype(np.float32)
    
    # 计算亮度缩放因子
    source_mean = np.mean(source_v)
    target_mean = np.mean(target_v)
    
    if source_mean > 0:
        brightness_factor = target_mean / source_mean
    else:
        brightness_factor = 1.0
    
    # 调整亮度
    enhancer = ImageEnhance.Brightness(source_img)
    result = enhancer.enhance(brightness_factor)
    
    print(f"📊 亮度调整因子: {brightness_factor:.2f}")
    print("✅ 亮度和对比度匹配完成!")
    return result

def process_images(source_path, target_path, output_path, match_type='all'):
    """
    处理图片的主函数
    match_type: 'color'=只匹配颜色, 'brightness'=只匹配亮度, 'all'=全部匹配
    """
    print("=" * 50)
    print("🦞 小龙虾图片处理工具")
    print("=" * 50)
    
    # 加载图片
    source_img = load_image(source_path)
    target_img = load_image(target_path)
    
    if source_img is None or target_img is None:
        print("❌ 图片加载失败，程序退出")
        return False
    
    # 根据匹配类型处理图片
    result_img = source_img.copy()
    
    if match_type in ['color', 'all']:
        result_img = match_color(result_img, target_img)
    
    if match_type in ['brightness', 'all']:
        result_img = match_brightness_contrast(result_img, target_img)
    
    # 保存结果
    success = save_image(result_img, output_path)
    
    if success:
        print("\n🎉 处理完成!")
        print(f"📁 源图片: {os.path.basename(source_path)}")
        print(f"📁 目标图片: {os.path.basename(target_path)}")
        print(f"📁 结果图片: {os.path.basename(output_path)}")
    else:
        print("\n❌ 处理失败!")
    
    return success

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description='将第二张图片处理得跟第一张一样')
    parser.add_argument('--source', '-s', required=True, help='源图片路径（要处理的图片）')
    parser.add_argument('--target', '-t', required=True, help='目标图片路径（要匹配的图片）')
    parser.add_argument('--output', '-o', default='result.jpg', help='输出图片路径（默认: result.jpg）')
    parser.add_argument('--type', '-T', choices=['color', 'brightness', 'all'], default='all',
                       help='匹配类型: color=颜色, brightness=亮度, all=全部（默认）')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.source):
        print(f"❌ 源图片不存在: {args.source}")
        return 1
    
    if not os.path.exists(args.target):
        print(f"❌ 目标图片不存在: {args.target}")
        return 1
    
    # 处理图片
    success = process_images(args.source, args.target, args.output, args.type)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())