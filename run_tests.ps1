$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".venv\Scripts\python.exe" -m pytest `
    tests `
    --html=reports\petstore-report.html `
    --self-contained-html
& ".venv\Scripts\python.exe" -m pytest `
    ui_tests `
    --html=reports\saucedemo-ui-report.html `
    --self-contained-html

Write-Host ""
Write-Host "API test report: reports\petstore-report.html"
Write-Host "UI test report: reports\saucedemo-ui-report.html"
