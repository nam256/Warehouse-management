# Backup SQLite database (dev)
$DbPath = Join-Path $PSScriptRoot "..\backend\oxeyns.db"
$BackupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Dest = Join-Path $BackupDir "oxeyns-$Stamp.db"
if (Test-Path $DbPath) {
  Copy-Item $DbPath $Dest
  Write-Host "Backup: $Dest"
} else {
  Write-Host "DB not found: $DbPath"
}
