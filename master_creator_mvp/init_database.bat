@echo off
REM Initialize Master Creator MVP Database
REM =======================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================
echo Master Creator MVP - Database Setup
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run initialization script
python init_database.py

echo.
pause
