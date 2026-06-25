@echo off
REM Launch the Voice Student Attendance app.
REM Creates the venv and installs deps on first run, then starts Streamlit.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo Starting Streamlit...
".venv\Scripts\python.exe" -m streamlit run app.py
