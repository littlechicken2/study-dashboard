$ErrorActionPreference = "Continue"
$Update = Join-Path $PSScriptRoot "update_dashboard.ps1"

while ($true) {
    try {
        & $Update
    } catch {
        Add-Content -LiteralPath (Join-Path $PSScriptRoot "update_error.log") -Value "$(Get-Date -Format s) $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 3600
}
