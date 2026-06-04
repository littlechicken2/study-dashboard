$Chrome = Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"
$Dashboard = "https://littlechicken2.github.io/study-dashboard/"
Start-Process -FilePath $Chrome -ArgumentList "--restore-last-session", $Dashboard
