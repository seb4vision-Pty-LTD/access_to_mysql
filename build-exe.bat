@echo off
REM Build PyInstaller Windows EXE
REM This script creates a standalone Access to MySQL Converter executable

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Building AccessToMySQL.exe
echo ========================================
echo.

REM Activate venv
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    echo Creating virtual environment first...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip setuptools
pip install -r backend\requirements.txt
pip install pyinstaller

REM Clean old builds
echo.
echo Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "AccessToMySQL.egg-info" rmdir /s /q AccessToMySQL.egg-info

REM Build the EXE using spec file
echo.
echo Building EXE with PyInstaller...
pyinstaller AccessToMySQL.spec

REM Check if build succeeded
if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check the output above for details.
    pause
    exit /b 1
)

REM Verify output exists
if not exist "dist\AccessToMySQL.exe" (
    echo.
    echo ERROR: EXE was not created!
    pause
    exit /b 1
)

REM Display results
echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Output: dist\AccessToMySQL.exe
echo Size: 
dir dist\AccessToMySQL.exe | findstr /i accesstomysql
echo.
echo Next steps:
echo 1. Test: .\dist\AccessToMySQL.exe
echo 2. Distribute: Copy dist\AccessToMySQL.exe to users
echo.
echo Users can just double-click to run!
echo.

pause
