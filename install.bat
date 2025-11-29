@echo off
REM AI CLI Installation Script for Windows (CMD)
REM This script installs AI CLI and its dependencies

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   AI CLI - Windows Installation (CMD)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure Python is properly installed with pip
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM Create virtual environment (optional but recommended)
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [WARNING] Could not create virtual environment
    echo Proceeding with system Python
) else (
    echo [OK] Virtual environment created
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [WARNING] Could not activate virtual environment
    ) else (
        echo [OK] Virtual environment activated
    )
)

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [OK] Installation completed successfully!
echo.
echo Next steps:
echo 1. Set your API key:
echo    python ai_cli.py --setup
echo.
echo 2. Or set environment variable:
echo    set OPENROUTER_API_KEY=your-api-key
echo.
echo 3. Run AI CLI:
echo    python ai_cli.py "your prompt here"
echo.
echo For interactive mode:
echo    python ai_cli.py
echo.
pause
