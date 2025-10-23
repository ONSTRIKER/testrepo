@echo off
echo ====================================
echo Discord Meeting Transcriber Bot
echo Building Windows Executable
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist DiscordMeetingTranscriber.exe del DiscordMeetingTranscriber.exe

echo.
echo [3/4] Building executable with PyInstaller...
echo This may take several minutes...
pyinstaller discord_meeting_bot.spec --clean
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Moving executable to main directory...
if exist dist\DiscordMeetingTranscriber.exe (
    move dist\DiscordMeetingTranscriber.exe .
    echo.
    echo ====================================
    echo BUILD SUCCESSFUL!
    echo ====================================
    echo.
    echo Executable created: DiscordMeetingTranscriber.exe
    echo.
    echo Next steps:
    echo 1. Create a .env file with your API keys
    echo 2. Run DiscordMeetingTranscriber.exe
    echo.
) else (
    echo ERROR: Executable not found after build
    pause
    exit /b 1
)

echo Cleaning up build files...
rmdir /s /q build
rmdir /s /q dist

echo.
echo Done! Press any key to exit...
pause >nul
