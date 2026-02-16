@echo off
REM Build script for creating distribution packages
REM Usage: build.bat [version]

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: build.bat [version]
    echo Example: build.bat 1.0.0
    exit /b 1
)

set VERSION=%1

echo.
echo ========================================
echo Building Access to MySQL Converter v%VERSION%
echo ========================================
echo.

REM Activate venv
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Install build tools
echo Installing build tools...
pip install --upgrade pip setuptools wheel build twine

REM Clean old builds
echo Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i" 2>nul

REM Update version in setup.py
echo Updating version to %VERSION%...
powershell -Command "(Get-Content setup.py) -replace '__version__ = \"[^\"]*\"', '__version__ = \"%VERSION%\"' | Set-Content setup.py"

REM Build distributions
echo.
echo Building source and wheel distributions...
python -m build

REM List output
echo.
echo ========================================
echo Build complete! Distribution files:
echo ========================================
dir dist\

echo.
echo Next steps:
echo 1. Test with: pip install dist\access-to-mysql-converter-%VERSION%-py3-none-any.whl
echo 2. Upload to GitHub: gh release create v%VERSION% dist/*
echo 3. Upload to PyPI: twine upload dist/*
echo.
echo Or use: python -m twine upload dist/*
echo.
