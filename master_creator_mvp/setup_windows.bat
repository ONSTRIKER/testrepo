@echo off
REM Master Creator MVP - Windows Setup Script
REM ==========================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================
echo Master Creator MVP - Windows Setup
echo ============================================
echo.
echo Working directory: %CD%
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python 3.11+ is installed
        pause
        exit /b 1
    )
    echo Virtual environment created!
) else (
    echo Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing core dependencies...
pip install --upgrade pip

REM Install core packages first (no compilation needed)
echo.
echo Installing Python packages (this may take a few minutes)...
pip install anthropic fastapi uvicorn pydantic python-dotenv sqlalchemy

REM Try to install psycopg2-binary (PostgreSQL driver)
echo.
echo Installing database driver...
pip install psycopg2-binary

REM Try to install other packages
pip install pandas numpy pytest requests httpx

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Anthropic API key
echo 2. Run: start_server.bat to launch the API
echo 3. Open browser to: http://localhost:8080/docs
echo.
pause
