# AI CLI Installation Script for Windows (PowerShell)
# This script installs AI CLI and its dependencies

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI CLI - Windows Installation (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[OK] pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip is not available" -ForegroundColor Red
    Write-Host "Please ensure Python is properly installed with pip" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create virtual environment (optional but recommended)
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
$venvPath = ".\venv"

if (Test-Path $venvPath) {
    Write-Host "[INFO] Virtual environment already exists" -ForegroundColor Yellow
} else {
    try {
        python -m venv venv
        Write-Host "[OK] Virtual environment created" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not create virtual environment" -ForegroundColor Yellow
        Write-Host "Proceeding with system Python" -ForegroundColor Yellow
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$activateScript = ".\venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    try {
        & $activateScript
        Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Could not activate virtual environment" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Virtual environment not found, using system Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan

try {
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "[OK] Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[OK] Installation completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Set your API key:" -ForegroundColor White
Write-Host "   python ai_cli.py --setup" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Or set environment variable:" -ForegroundColor White
Write-Host "   `$env:OPENROUTER_API_KEY='your-api-key'" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Run AI CLI:" -ForegroundColor White
Write-Host "   python ai_cli.py `"your prompt here`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "For interactive mode:" -ForegroundColor White
Write-Host "   python ai_cli.py" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
