$Script = Join-Path $PSScriptRoot "monitor_desktop_activity.py"
Start-Process -FilePath "python" -ArgumentList "`"$Script`"" -WindowStyle Hidden
