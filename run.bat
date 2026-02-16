@echo off
REM Access to MySQL Converter - Windows Startup Script
REM This script activates the virtual environment, installs dependencies, and starts the app

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Access to MySQL Converter - Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip setuptools wheel
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Start the app
echo.
echo ========================================
echo Starting Access to MySQL Converter
echo ========================================
echo.
echo Server running at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

cd /d "%cd%"
python -m waitress --port=5000 --host=0.0.0.0 backend.app:app

pause
