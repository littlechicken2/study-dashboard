$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
python (Join-Path $PSScriptRoot "collect_progress.py")

if (Test-Path (Join-Path $Root ".git")) {
    git -C $Root add data/progress.json data/course_progress.json data/reading_log.json data/reading_progress.json
    if (-not (git -C $Root diff --cached --quiet)) {
        git -C $Root commit -m "Update study progress"
        git -C $Root push
    }
}
