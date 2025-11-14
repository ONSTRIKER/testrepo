@echo off
REM Install PostgreSQL driver for Python
REM ======================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo Working directory: %CD%
echo.
echo Installing psycopg2-binary (PostgreSQL driver)...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install psycopg2-binary
pip install psycopg2-binary

if errorlevel 1 (
    echo.
    echo ============================================
    echo Installation failed!
    echo ============================================
    echo.
    echo Don't worry - since you're using SQLite, we can make psycopg2 optional.
    echo Let me know and I'll update the code to skip psycopg2.
    echo.
) else (
    echo.
    echo ============================================
    echo Successfully installed psycopg2-binary!
    echo ============================================
    echo.
    echo You can now run: start_server.bat
    echo.
)

pause
