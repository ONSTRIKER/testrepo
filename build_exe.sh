#!/bin/bash

echo "===================================="
echo "Discord Meeting Transcriber Bot"
echo "Building Executable"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/4] Cleaning previous build..."
rm -rf build dist DiscordMeetingTranscriber

echo ""
echo "[3/4] Building executable with PyInstaller..."
echo "This may take several minutes..."
pyinstaller discord_meeting_bot.spec --clean
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "[4/4] Moving executable to main directory..."
if [ -f "dist/DiscordMeetingTranscriber" ]; then
    mv dist/DiscordMeetingTranscriber .
    chmod +x DiscordMeetingTranscriber
    echo ""
    echo "===================================="
    echo "BUILD SUCCESSFUL!"
    echo "===================================="
    echo ""
    echo "Executable created: DiscordMeetingTranscriber"
    echo ""
    echo "Next steps:"
    echo "1. Create a .env file with your API keys"
    echo "2. Run ./DiscordMeetingTranscriber"
    echo ""
else
    echo "ERROR: Executable not found after build"
    exit 1
fi

echo "Cleaning up build files..."
rm -rf build dist

echo ""
echo "Done!"
