@echo off
REM Master Creator MVP - Start Server Script
REM =========================================

echo.
echo ============================================
echo Master Creator MVP - Starting Server
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file has API key configured
findstr /C:"your_anthropic_api_key_here" .env >nul 2>&1
if %errorlevel% == 0 (
    echo.
    echo ============================================
    echo WARNING: API Key Not Configured!
    echo ============================================
    echo.
    echo Please edit .env file and add your Anthropic API key:
    echo   1. Open .env in Notepad
    echo   2. Replace "your_anthropic_api_key_here" with your actual key
    echo   3. Save the file
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo Starting API server...
echo Server will be available at: http://localhost:8080
echo API Documentation: http://localhost:8080/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Set PYTHONPATH to current directory so Python can find 'src' module
set PYTHONPATH=%CD%

REM Start the server (no reload for Windows stability)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080

pause
