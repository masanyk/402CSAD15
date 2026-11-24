param([string]$Pdf, [string]$OutPrefix, [int]$Width = 1800)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$asAct = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
function Await($op, [Type]$t) { $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(); $task.Result }
[void][Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
[void][Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($Pdf)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$dir = Split-Path $OutPrefix -Parent; $base = Split-Path $OutPrefix -Leaf
$folder = Await ([Windows.Storage.StorageFolder]::GetFolderFromPathAsync($dir)) ([Windows.Storage.StorageFolder])
for ($i = 0; $i -lt $doc.PageCount; $i++) {
  $page = $doc.GetPage($i)
  $name = if ($doc.PageCount -eq 1) { "$base.png" } else { "$base-$($i+1).png" }
  $out = Await ($folder.CreateFileAsync($name, 1)) ([Windows.Storage.StorageFile])
  $st = Await ($out.OpenAsync(1)) ([Windows.Storage.Streams.IRandomAccessStream])
  $opt = New-Object Windows.Data.Pdf.PdfPageRenderOptions; $opt.DestinationWidth = $Width
  $bg = New-Object Windows.UI.Color; $bg.A = 255; $bg.R = 255; $bg.G = 255; $bg.B = 255; $opt.BackgroundColor = $bg
  $t = $asAct.Invoke($null, @($page.RenderToStreamAsync($st, $opt))); $t.Wait(); $st.Dispose()
}
"pages: $($doc.PageCount)"
