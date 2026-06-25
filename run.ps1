# Launch the Voice Student Attendance app (PowerShell).
# Creates the venv and installs deps on first run, then starts Streamlit.

Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    Write-Host "Installing dependencies..."
    & ".venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
}

Write-Host "Starting Streamlit..."
& ".venv\Scripts\python.exe" -m streamlit run app.py
