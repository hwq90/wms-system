# 🦞 小龙虾图片处理工具 - PowerShell版
# 不需要安装Python，使用.NET内置功能

Write-Host "🦞 小龙虾图片颜色匹配工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 设置图片路径
$sourceImage = "C:\Users\Administrator\clawd\第二张图片.png"
$targetImage = "C:\Users\Administrator\clawd\第一张图片.png"
$outputImage = "C:\Users\Administrator\clawd\处理结果.png"

Write-Host ""
Write-Host "📁 源图片（要处理的）: $(Split-Path $sourceImage -Leaf)"
Write-Host "📁 目标图片（要匹配的）: $(Split-Path $targetImage -Leaf)"
Write-Host "📁 输出图片: $(Split-Path $outputImage -Leaf)"
Write-Host ""

# 检查文件是否存在
if (-not (Test-Path $sourceImage)) {
    Write-Host "❌ 源图片不存在: $sourceImage" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $targetImage)) {
    Write-Host "❌ 目标图片不存在: $targetImage" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 开始处理图片..." -ForegroundColor Green

try {
    # 加载.NET绘图程序集
    Add-Type -AssemblyName System.Drawing
    
    # 加载图片
    $sourceBitmap = [System.Drawing.Bitmap]::FromFile($sourceImage)
    $targetBitmap = [System.Drawing.Bitmap]::FromFile($targetImage)
    
    Write-Host "📊 图片信息:" -ForegroundColor Yellow
    Write-Host "   源图片: $($sourceBitmap.Width)x$($sourceBitmap.Height), $($sourceBitmap.PixelFormat)"
    Write-Host "   目标图片: $($targetBitmap.Width)x$($targetBitmap.Height), $($targetBitmap.PixelFormat)"
    
    # 创建新的位图（与源图片相同尺寸）
    $resultBitmap = New-Object System.Drawing.Bitmap $sourceBitmap.Width, $sourceBitmap.Height
    
    # 简单的颜色匹配算法
    Write-Host "🎨 进行颜色匹配..." -ForegroundColor Yellow
    
    # 计算目标图片的平均颜色
    $targetAvgColor = [System.Drawing.Color]::Empty
    $totalR = 0
    $totalG = 0
    $totalB = 0
    $pixelCount = $targetBitmap.Width * $targetBitmap.Height
    
    # 采样计算平均颜色（为了性能，只采样部分像素）
    $sampleStep = [Math]::Max(1, [Math]::Sqrt($pixelCount) / 10)
    $sampledCount = 0
    
    for ($x = 0; $x -lt $targetBitmap.Width; $x += $sampleStep) {
        for ($y = 0; $y -lt $targetBitmap.Height; $y += $sampleStep) {
            $color = $targetBitmap.GetPixel($x, $y)
            $totalR += $color.R
            $totalG += $color.G
            $totalB += $color.B
            $sampledCount++
        }
    }
    
    $avgR = [Math]::Round($totalR / $sampledCount)
    $avgG = [Math]::Round($totalG / $sampledCount)
    $avgB = [Math]::Round($totalB / $sampledCount)
    $targetAvgColor = [System.Drawing.Color]::FromArgb($avgR, $avgG, $avgB)
    
    Write-Host "📊 目标图片平均颜色: R=$avgR, G=$avgG, B=$avgB" -ForegroundColor Cyan
    
    # 计算源图片的平均颜色
    $sourceAvgColor = [System.Drawing.Color]::Empty
    $totalR = 0
    $totalG = 0
    $totalB = 0
    $sampledCount = 0
    
    for ($x = 0; $x -lt $sourceBitmap.Width; $x += $sampleStep) {
        for ($y = 0; $y -lt $sourceBitmap.Height; $y += $sampleStep) {
            $color = $sourceBitmap.GetPixel($x, $y)
            $totalR += $color.R
            $totalG += $color.G
            $totalB += $color.B
            $sampledCount++
        }
    }
    
    $sourceAvgR = [Math]::Round($totalR / $sampledCount)
    $sourceAvgG = [Math]::Round($totalG / $sampledCount)
    $sourceAvgB = [Math]::Round($totalB / $sampledCount)
    
    Write-Host "📊 源图片平均颜色: R=$sourceAvgR, G=$sourceAvgG, B=$sourceAvgB" -ForegroundColor Cyan
    
    # 计算颜色调整因子
    $adjustR = if ($sourceAvgR -ne 0) { $avgR / $sourceAvgR } else { 1 }
    $adjustG = if ($sourceAvgG -ne 0) { $avgG / $sourceAvgG } else { 1 }
    $adjustB = if ($sourceAvgB -ne 0) { $avgB / $sourceAvgB } else { 1 }
    
    Write-Host "📊 颜色调整因子: R=$([Math]::Round($adjustR,2)), G=$([Math]::Round($adjustG,2)), B=$([Math]::Round($adjustB,2))" -ForegroundColor Magenta
    
    # 应用颜色调整到每个像素
    Write-Host "🔄 应用颜色调整..." -ForegroundColor Yellow
    $progress = 0
    $totalPixels = $sourceBitmap.Width * $sourceBitmap.Height
    
    for ($x = 0; $x -lt $sourceBitmap.Width; $x++) {
        for ($y = 0; $y -lt $sourceBitmap.Height; $y++) {
            $color = $sourceBitmap.GetPixel($x, $y)
            
            # 调整每个颜色通道
            $newR = [Math]::Min(255, [Math]::Max(0, [Math]::Round($color.R * $adjustR)))
            $newG = [Math]::Min(255, [Math]::Max(0, [Math]::Round($color.G * $adjustG)))
            $newB = [Math]::Min(255, [Math]::Max(0, [Math]::Round($color.B * $adjustB)))
            
            $newColor = [System.Drawing.Color]::FromArgb($color.A, $newR, $newG, $newB)
            $resultBitmap.SetPixel($x, $y, $newColor)
            
            # 更新进度（每1000像素更新一次）
            $progress++
            if ($progress % 1000 -eq 0) {
                $percent = [Math]::Round(($progress / $totalPixels) * 100)
                Write-Progress -Activity "处理图片" -Status "$percent% 完成" -PercentComplete $percent
            }
        }
    }
    
    Write-Progress -Activity "处理图片" -Completed
    
    # 保存结果
    $resultBitmap.Save($outputImage, [System.Drawing.Imaging.ImageFormat]::Png)
    
    # 释放资源
    $sourceBitmap.Dispose()
    $targetBitmap.Dispose()
    $resultBitmap.Dispose()
    
    Write-Host ""
    Write-Host "✅ 处理完成！" -ForegroundColor Green
    Write-Host "📁 结果已保存到: $outputImage" -ForegroundColor Yellow
    
    # 显示文件信息
    $resultFile = Get-Item $outputImage
    Write-Host "📏 文件大小: $([Math]::Round($resultFile.Length/1KB,2)) KB" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "❌ 处理失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎯 操作完成！" -ForegroundColor Green
Write-Host "1. 图片已保存在工作空间目录" -ForegroundColor White
Write-Host "2. 文件名为: 处理结果.png" -ForegroundColor White
Write-Host "3. 你可以查看并确认效果" -ForegroundColor White