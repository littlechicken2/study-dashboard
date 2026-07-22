$ErrorActionPreference = "SilentlyContinue"

$ResetReading = Join-Path $PSScriptRoot "reset_reading_session.py"
$ActivityMonitor = Join-Path $PSScriptRoot "monitor_desktop_activity.py"
$Watcher = Join-Path $PSScriptRoot "watch_dashboard.ps1"
$Chrome = Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"
$LocalIndex = "file:///D:/WOK/POKESTOP/index.html"

function Start-HiddenProcess {
    param([string]$FilePath, [string[]]$ArgumentList)
    if (Get-Command $FilePath -ErrorAction SilentlyContinue) {
        Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WindowStyle Hidden
    }
}

function Test-ChromeSessionContains {
    param([string]$Url)

    $ChromeData = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
    $Profiles = Get-ChildItem -LiteralPath $ChromeData -Directory -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -eq "Default" -or $_.Name -like "Profile *"
    }

    foreach ($Profile in $Profiles) {
        $Sessions = Join-Path $Profile.FullName "Sessions"
        foreach ($SessionFile in Get-ChildItem -LiteralPath $Sessions -File -ErrorAction SilentlyContinue) {
            try {
                $Content = [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($SessionFile.FullName))
                if ($Content.Contains($Url)) { return $true }
            } catch {
                continue
            }
        }
    }
    return $false
}

Start-HiddenProcess -FilePath "python.exe" -ArgumentList @($ResetReading)
Start-HiddenProcess -FilePath "python.exe" -ArgumentList @($ActivityMonitor)
Start-HiddenProcess -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", $Watcher
)

Start-Sleep -Seconds 3

$HasLocalIndex = Test-ChromeSessionContains -Url $LocalIndex
$ChromeRunning = Get-Process chrome -ErrorAction SilentlyContinue

if (-not $ChromeRunning) {
    $ChromeArguments = @("--restore-last-session")
    if (-not $HasLocalIndex) { $ChromeArguments += $LocalIndex }
    Start-Process -FilePath $Chrome -ArgumentList $ChromeArguments
} elseif (-not $HasLocalIndex) {
    Start-Process -FilePath $Chrome -ArgumentList $LocalIndex
}
