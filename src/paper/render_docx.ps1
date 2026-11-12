# render_docx.ps1: render a DOCX to PDF with Word COM (the real Word layout), then report the page count.
# Usage (PowerShell 5.1): powershell -File src\paper\render_docx.ps1 -Docx <abs path> -Pdf <abs path>
param(
  [Parameter(Mandatory=$true)][string]$Docx,
  [Parameter(Mandatory=$true)][string]$Pdf
)
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($Docx, $false, $true)
  $doc.Repaginate()
  $pages = $doc.ComputeStatistics(2)
  $words = $doc.ComputeStatistics(0)
  $doc.ExportAsFixedFormat($Pdf, 17)
  $doc.Close($false)
  Write-Output ("rendered pages=" + $pages + " words=" + $words + " -> " + $Pdf)
} finally {
  $word.Quit()
}
