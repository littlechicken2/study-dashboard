$ErrorActionPreference = "Stop"
$Watcher = Join-Path $PSScriptRoot "watch_dashboard.ps1"
$ResetReading = Join-Path $PSScriptRoot "reset_reading_session.py"
$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "StudyDashboardUpdater.vbs"
$Chrome = Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"
$Dashboard = "https://littlechicken2.github.io/study-dashboard/"
$Commands = @(
    "Set shell = CreateObject(""WScript.Shell"")",
    "shell.Run ""python "" & Chr(34) & ""$ResetReading"" & Chr(34), 0, True",
    "shell.Run ""powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "" & Chr(34) & ""$Watcher"" & Chr(34), 0, False",
    "WScript.Sleep 3000",
    "shell.Run Chr(34) & ""$Chrome"" & Chr(34) & "" --restore-last-session "" & Chr(34) & ""$Dashboard"" & Chr(34), 1, False"
)
Set-Content -LiteralPath $Launcher -Value $Commands -Encoding ASCII
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", "`"$Watcher`"" -WindowStyle Hidden
Write-Host "Installed the hourly updater and Chrome session/dashboard launcher."
