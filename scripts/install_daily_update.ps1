$ErrorActionPreference = "Stop"
$Watcher = Join-Path $PSScriptRoot "watch_dashboard.ps1"
$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "StudyDashboardUpdater.vbs"
$Command = "CreateObject(""WScript.Shell"").Run ""powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """"""$Watcher"""""""", 0, False"
Set-Content -LiteralPath $Launcher -Value $Command -Encoding ASCII
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", "`"$Watcher`"" -WindowStyle Hidden
Write-Host "Installed the hourly dashboard updater. It starts automatically when you sign in."
