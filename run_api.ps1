$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
$env:DEMO_MODE = "1"
& ".venv\Scripts\python.exe" -m app.server --host 127.0.0.1 --port 5000
