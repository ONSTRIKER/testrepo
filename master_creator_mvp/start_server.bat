@echo off
REM Master Creator MVP - Start Server Script
REM =========================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================
echo Master Creator MVP - Starting Server
echo ============================================
echo.
echo Working directory: %CD%
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

REM Start the server using Python launcher script
python run_server.py

pause
