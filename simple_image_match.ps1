# 简单图片颜色匹配工具
Write-Host "🦞 小龙虾图片处理工具" -ForegroundColor Cyan

# 图片路径
$img1 = "C:\Users\Administrator\clawd\第一张图片.png"
$img2 = "C:\Users\Administrator\clawd\第二张图片.png"
$output = "C:\Users\Administrator\clawd\匹配结果.png"

Write-Host "处理中..."
Write-Host "源图片: $img2"
Write-Host "目标图片: $img1"
Write-Host "输出: $output"

try {
    # 加载.NET绘图库
    Add-Type -AssemblyName System.Drawing
    
    # 加载图片
    $bitmap1 = [System.Drawing.Bitmap]::FromFile($img1)
    $bitmap2 = [System.Drawing.Bitmap]::FromFile($img2)
    
    # 创建结果位图
    $result = New-Object System.Drawing.Bitmap $bitmap2.Width, $bitmap2.Height
    
    # 简单颜色调整：匹配平均亮度
    # 计算图片1的平均亮度
    $totalBrightness1 = 0
    $count1 = 0
    for ($x = 0; $x -lt $bitmap1.Width; $x += 10) {
        for ($y = 0; $y -lt $bitmap1.Height; $y += 10) {
            $color = $bitmap1.GetPixel($x, $y)
            $brightness = ($color.R + $color.G + $color.B) / 3
            $totalBrightness1 += $brightness
            $count1++
        }
    }
    $avgBrightness1 = $totalBrightness1 / $count1
    
    # 计算图片2的平均亮度
    $totalBrightness2 = 0
    $count2 = 0
    for ($x = 0; $x -lt $bitmap2.Width; $x += 10) {
        for ($y = 0; $y -lt $bitmap2.Height; $y += 10) {
            $color = $bitmap2.GetPixel($x, $y)
            $brightness = ($color.R + $color.G + $color.B) / 3
            $totalBrightness2 += $brightness
            $count2++
        }
    }
    $avgBrightness2 = $totalBrightness2 / $count2
    
    Write-Host "图片1平均亮度: $avgBrightness1"
    Write-Host "图片2平均亮度: $avgBrightness2"
    
    # 计算调整因子
    if ($avgBrightness2 -gt 0) {
        $adjustFactor = $avgBrightness1 / $avgBrightness2
    } else {
        $adjustFactor = 1
    }
    
    Write-Host "亮度调整因子: $adjustFactor"
    
    # 应用调整
    for ($x = 0; $x -lt $bitmap2.Width; $x++) {
        for ($y = 0; $y -lt $bitmap2.Height; $y++) {
            $color = $bitmap2.GetPixel($x, $y)
            
            # 调整每个颜色通道
            $newR = [Math]::Min(255, [Math]::Max(0, [int]($color.R * $adjustFactor)))
            $newG = [Math]::Min(255, [Math]::Max(0, [int]($color.G * $adjustFactor)))
            $newB = [Math]::Min(255, [Math]::Max(0, [int]($color.B * $adjustFactor)))
            
            $newColor = [System.Drawing.Color]::FromArgb($color.A, $newR, $newG, $newB)
            $result.SetPixel($x, $y, $newColor)
        }
    }
    
    # 保存结果
    $result.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
    
    # 清理资源
    $bitmap1.Dispose()
    $bitmap2.Dispose()
    $result.Dispose()
    
    Write-Host "✅ 处理完成！结果保存在: $output" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 错误: $_" -ForegroundColor Red
}