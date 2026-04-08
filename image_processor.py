#!/usr/bin/env python3
"""
图片处理工具
可以调整大小、颜色、亮度、对比度等
"""

import os
import sys
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

def load_image(image_path):
    """加载图片"""
    try:
        img = Image.open(image_path)
        print(f"成功加载图片: {image_path}")
        print(f"图片格式: {img.format}, 尺寸: {img.size}, 模式: {img.mode}")
        return img
    except Exception as e:
        print(f"加载图片失败: {e}")
        return None

def save_image(image, output_path):
    """保存图片"""
    try:
        image.save(output_path)
        print(f"图片已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存图片失败: {e}")
        return False

def resize_image(image, target_size):
    """调整图片尺寸"""
    return image.resize(target_size, Image.Resampling.LANCZOS)

def match_color(source_img, target_img):
    """
    将目标图片的颜色匹配到源图片
    简单的颜色匹配算法
    """
    # 转换为RGB（如果图片有alpha通道）
    if source_img.mode != 'RGB':
        source_img = source_img.convert('RGB')
    if target_img.mode != 'RGB':
        target_img = target_img.convert('RGB')
    
    # 计算源图片和目标图片的颜色统计
    source_stats = get_image_stats(source_img)
    target_stats = get_image_stats(target_img)
    
    # 简单的颜色调整：匹配均值和标准差
    source_array = np.array(source_img).astype(np.float32)
    target_array = np.array(target_img).astype(np.float32)
    
    # 对每个通道进行颜色匹配
    for channel in range(3):
        source_mean = source_stats['mean'][channel]
        source_std = source_stats['std'][channel]
        target_mean = target_stats['mean'][channel]
        target_std = target_stats['std'][channel]
        
        # 避免除零
        if target_std > 0:
            # 颜色匹配公式
            source_array[:, :, channel] = (source_array[:, :, channel] - source_mean) * (target_std / source_std) + target_mean
    
    # 确保值在0-255范围内
    source_array = np.clip(source_array, 0, 255)
    
    return Image.fromarray(source_array.astype(np.uint8))

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

def adjust_brightness(image, factor):
    """调整亮度"""
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

def adjust_contrast(image, factor):
    """调整对比度"""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def adjust_saturation(image, factor):
    """调整饱和度"""
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def apply_blur(image, radius=2):
    """应用模糊效果"""
    return image.filter(ImageFilter.GaussianBlur(radius))

def convert_format(image, format='JPEG'):
    """转换图片格式"""
    if format == 'JPEG' and image.mode in ['RGBA', 'LA']:
        # JPEG不支持alpha通道，需要转换为RGB
        image = image.convert('RGB')
    return image

def main():
    """主函数"""
    print("=== 图片处理工具 ===")
    print("功能:")
    print("1. 调整尺寸")
    print("2. 颜色匹配")
    print("3. 调整亮度/对比度/饱和度")
    print("4. 应用模糊效果")
    print("5. 格式转换")
    
    # 这里可以添加交互式代码，但为了简单起见，我们先提供一个示例
    print("\n示例用法:")
    print("python image_processor.py --source 图片1.jpg --target 图片2.jpg --output 结果.jpg --match-color")
    
if __name__ == "__main__":
    main()