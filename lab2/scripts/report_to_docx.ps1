param([string]$Html, [string]$Docx, [string]$Pdf)
# Відкриває HTML у Word, вбудовує зображення в документ, зберігає .docx і .pdf
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($Html, $false, $false)
  foreach ($s in @($d.InlineShapes)) {
    if ($s.LinkFormat -ne $null) { $s.LinkFormat.SavePictureWithDocument = $true; $s.LinkFormat.BreakLink() }
  }
  $d.SaveAs2($Docx, 16)          # wdFormatXMLDocument
  $d.Close(0)
  $d = $w.Documents.Open($Docx, $false, $true)
  $d.ExportAsFixedFormat($Pdf, 17)
  "pages: " + $d.ComputeStatistics(2)
  $d.Close(0)
} finally { $w.Quit() }
