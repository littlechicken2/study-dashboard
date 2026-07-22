$ErrorActionPreference = "Stop"
$Launcher = Join-Path $PSScriptRoot "start_dashboard_session.ps1"
$Startup = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $Startup "Study Dashboard.lnk"
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Launcher`""
$Shortcut.WorkingDirectory = Split-Path -Parent $Launcher
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Restore Chrome and start the study dashboard background services"
$Shortcut.Save()

Remove-Item -LiteralPath (Join-Path $Startup "StudyDashboardUpdater.vbs") -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $Startup "StudyDashboardUpdater.vbs.bak-20260717") -Force -ErrorAction SilentlyContinue

Write-Host "Installed the hidden dashboard startup shortcut."
