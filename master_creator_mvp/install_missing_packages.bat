@echo off
REM Install missing Python packages
REM ================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ============================================
echo Installing Missing Packages
echo ============================================
echo.
echo Working directory: %CD%
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install python-multipart (needed for file uploads)
echo Installing python-multipart...
pip install python-multipart

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo You can now run: start_server.bat
echo.
pause
