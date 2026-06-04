$ErrorActionPreference = "Stop"
$Watcher = Join-Path $PSScriptRoot "watch_dashboard.ps1"
$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "StudyDashboardUpdater.vbs"
$Chrome = Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"
$Dashboard = "https://littlechicken2.github.io/study-dashboard/"
$Commands = @(
    "Set shell = CreateObject(""WScript.Shell"")",
    "shell.Run ""powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """"""$Watcher"""""""", 0, False",
    "WScript.Sleep 3000",
    "shell.Run """"""$Chrome"""" --restore-last-session """"""$Dashboard"""""""", 1, False"
)
Set-Content -LiteralPath $Launcher -Value $Commands -Encoding ASCII
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", "`"$Watcher`"" -WindowStyle Hidden
Write-Host "Installed the hourly updater and Chrome session/dashboard launcher."
