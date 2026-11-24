param([string]$In, [string]$Out, [int]$Margin = 30)
# Обрізає PNG до області з не-білими пікселями (для зображення плати на аркуші A4).
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile($In)
$minX = $bmp.Width; $minY = $bmp.Height; $maxX = 0; $maxY = 0
for ($y = 0; $y -lt $bmp.Height; $y += 2) {
  for ($x = 0; $x -lt $bmp.Width; $x += 2) {
    $c = $bmp.GetPixel($x, $y)
    if ($c.A -gt 20 -and ($c.R -lt 235 -or $c.G -lt 235 -or $c.B -lt 235)) {
      if ($x -lt $minX) { $minX = $x }; if ($x -gt $maxX) { $maxX = $x }
      if ($y -lt $minY) { $minY = $y }; if ($y -gt $maxY) { $maxY = $y }
    }
  }
}
$minX = [Math]::Max(0, $minX - $Margin); $minY = [Math]::Max(0, $minY - $Margin)
$maxX = [Math]::Min($bmp.Width - 1, $maxX + $Margin); $maxY = [Math]::Min($bmp.Height - 1, $maxY + $Margin)
$rect = New-Object System.Drawing.Rectangle $minX, $minY, ($maxX - $minX), ($maxY - $minY)
$crop = $bmp.Clone($rect, $bmp.PixelFormat)
$bmp.Dispose()
$crop.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose()
"cropped to $($rect.Width)x$($rect.Height)"
