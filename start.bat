@echo off
title CvSU Bacoor - Online Enrollment System
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo First-time setup: creating virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo.
        echo Python was not found. Install Python 3.12 from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH" during installation.
        pause
        exit /b 1
    )
    echo Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
)

echo.
echo Starting CvSU Bacoor Online Enrollment at http://127.0.0.1:8000/
echo Keep this window open while you use the site. Press Ctrl+C to stop.
echo.

start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000/"
".venv\Scripts\python.exe" manage.py runserver

pause
