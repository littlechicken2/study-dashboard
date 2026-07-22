$Launcher = Join-Path $PSScriptRoot "start_dashboard_session.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", $Launcher
) -WindowStyle Hidden
