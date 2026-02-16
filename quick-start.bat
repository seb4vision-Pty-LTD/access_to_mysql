@echo off
echo ================================================
echo   Access to MySQL Migration Tool - Quick Start
echo ================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo X Node.js is not installed. Please install Node.js first.
    echo   Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo √ Node.js found
node --version

REM Check if npm is installed
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo X npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo √ npm found
npm --version

REM Install dependencies
echo.
echo Installing dependencies...
call npm install

if %errorlevel% equ 0 (
    echo √ Dependencies installed successfully!
) else (
    echo X Failed to install dependencies
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "configs" mkdir configs
echo √ Directories created

echo.
echo ================================================
echo   ✨ Setup Complete!
echo ================================================
echo.
echo To start the application:
echo   npm start
echo.
echo Then open your browser to:
echo   http://localhost:3000
echo.
echo Make sure MySQL is running before connecting!
echo ================================================
echo.
pause
