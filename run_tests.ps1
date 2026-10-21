$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".venv\Scripts\python.exe" -m pytest `
    --html=reports\report.html `
    --self-contained-html

Write-Host ""
Write-Host "HTML report: reports\report.html"
