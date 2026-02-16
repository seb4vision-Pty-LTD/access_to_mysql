@echo off
REM Access to MySQL Converter - Windows Installation Script

echo ==========================================
echo Access to MySQL Converter - Setup
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Check pip installation
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed
    echo Installing pip...
    python -m ensurepip --default-pip
)
echo [OK] pip is available
echo.


REM Check for virtual environment
echo Checking for virtual environment...
if not exist ".venv\Scripts\activate" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment 
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.


REM Install Python dependencies
echo Installing Python dependencies...
cd backend
pip install -r "requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed successfully
cd ..
echo.

REM Check MySQL installation
echo Checking MySQL installation...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MySQL not found in PATH
    echo Please ensure MySQL is installed and running
    echo Download from: https://dev.mysql.com/downloads/installer/
) else (
    mysql --version
    echo [OK] MySQL found
)
echo.

REM Check for Access ODBC drivers
echo Checking for Access ODBC drivers...
echo Please ensure you have Microsoft Access Database Engine installed
echo Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920
echo Note: Choose the version (32-bit or 64-bit) that matches your Python installation
echo.

REM Create necessary directories
echo Creating directories...
if not exist "data\uploads" mkdir data\uploads
if not exist "configs" mkdir configs
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

REM Create .env file
if not exist "backend\.env" (
    echo Creating .env file...
    copy backend\.env.example backend\.env
    echo [OK] .env file created - please edit with your settings
) else (
    echo [INFO] .env file already exists
)
echo.

REM Test backend imports
echo Testing backend dependencies...
cd backend
python -c "import flask; import pymysql; import pyodbc; import pandas; print('[OK] All imports successful')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may have issues
    echo This could be due to missing ODBC drivers
)
cd ..
echo.

echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Install Microsoft Access Database Engine (if not already installed)
echo    Download: https://www.microsoft.com/en-us/download/details.aspx?id=54920
echo 2. Edit backend\.env with your MySQL configuration
echo 3. Start the backend: python app.py
echo 4. Open frontend\index.html in your browser
echo.
echo For detailed instructions, see README.md
echo.
pause

REM Opening Backend
start cmd /k "cd backend && python app.py"

