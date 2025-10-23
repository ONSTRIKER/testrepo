# Building Windows Executable (.exe)

This guide will help you create a standalone Windows executable that doesn't require Python to be installed.

## Prerequisites

**Only needed for building** (not for running the .exe):
- Windows 10/11 (or Linux/macOS for their respective executables)
- Python 3.8 or higher installed
- Internet connection for downloading dependencies

## Quick Build (Windows)

### Option 1: Automated Build Script

1. **Double-click** `build_exe.bat`
2. Wait for the build to complete (5-10 minutes)
3. Find `DiscordMeetingTranscriber.exe` in the same folder

That's it!

### Option 2: Manual Build

```cmd
# Install dependencies
pip install -r requirements.txt

# Build the executable
pyinstaller discord_meeting_bot.spec --clean

# Find the .exe in the dist folder
# Move it to your desired location
```

## Quick Build (Linux/macOS)

```bash
# Make the build script executable
chmod +x build_exe.sh

# Run the build script
./build_exe.sh

# Find the executable in the main folder
# Run with: ./DiscordMeetingTranscriber
```

## Using the Executable

### First Time Setup

1. **Create a `.env` file** in the same folder as the .exe:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

2. **Install FFmpeg** (required for audio processing):
   - Download from: https://ffmpeg.org/download.html
   - Add to Windows PATH or place `ffmpeg.exe` in the same folder

3. **Create folders** (or let the bot create them automatically):
   - `recordings/` - for audio files
   - `transcripts/` - for transcripts and summaries

### Running the Bot

**Windows:**
- Double-click `DiscordMeetingTranscriber.exe`
- Or run from Command Prompt: `DiscordMeetingTranscriber.exe`

**Linux/macOS:**
```bash
./DiscordMeetingTranscriber
```

You should see:
```
Starting Discord Meeting Transcriber Bot...
YourBot#1234 has connected to Discord!
Ready to transcribe meetings!
```

The bot will keep running in the terminal window. **Don't close it** while you want the bot online.

## Distribution

If you want to share the bot with others who don't have Python:

### What to Include:

1. `DiscordMeetingTranscriber.exe` (or the Linux/macOS executable)
2. `.env.example` (rename to `.env` and fill in API keys)
3. `README.md` or create a simple usage guide

### What Recipients Need:

- **FFmpeg** installed (https://ffmpeg.org/download.html)
- **Discord Bot Token** (they need to create their own bot)
- **OpenAI API Key** (for Whisper transcription)
- **Anthropic API Key** (for Claude summaries)

### Simple User Instructions:

```
1. Download FFmpeg and add to PATH
2. Create a .env file with your API keys
3. Run DiscordMeetingTranscriber.exe
4. Use !join, !record, !stop in Discord
```

## Troubleshooting

### Build Issues

**"Python not found"**
- Install Python from https://www.python.org/
- Make sure "Add Python to PATH" was checked during installation

**"pip not found"**
```cmd
python -m ensurepip --upgrade
```

**Build fails with module errors**
```cmd
pip install -r requirements.txt --upgrade
```

**Build takes forever**
- This is normal! PyInstaller analyzes all dependencies
- First build: 5-10 minutes
- Subsequent builds: 2-5 minutes

### Runtime Issues

**"FFmpeg not found"**
- Install FFmpeg: https://ffmpeg.org/download.html
- Add to PATH or place `ffmpeg.exe` in the same folder as the .exe

**"API key not found"**
- Make sure `.env` file is in the **same folder** as the .exe
- Check that `.env` has no typos (not `.env.txt`)

**Bot doesn't respond**
- Check the bot is online in Discord (shows as online)
- Verify bot permissions (Connect, Speak, Send Messages)
- Make sure you're using the correct command prefix: `!`

**Recording fails**
- Ensure FFmpeg is properly installed
- Check disk space for recordings
- Verify bot has permission to write to `recordings/` folder

### Executable Size

The .exe will be around **80-150 MB** because it includes:
- Python interpreter
- All required libraries
- Discord.py and dependencies

This is normal for PyInstaller executables!

## Advanced: Custom Build Options

### Change Icon

1. Get a `.ico` file (Windows icon)
2. Edit `discord_meeting_bot.spec`:
   ```python
   icon='path/to/your/icon.ico',
   ```
3. Rebuild with `pyinstaller discord_meeting_bot.spec --clean`

### Reduce File Size

Edit `discord_meeting_bot.spec`:
```python
upx=True,  # Enable UPX compression (may not work on all systems)
```

Install UPX:
- Download from: https://upx.github.io/
- Add to PATH

### Create Installer

Use a tool like Inno Setup or NSIS to create a proper installer:
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **NSIS**: https://nsis.sourceforge.io/

## Security Notes

### For Builders:
- **Never** include your `.env` file with API keys in the distribution
- Only share `.env.example` as a template

### For Users:
- The .exe is **not signed**, so Windows may show a warning
- This is normal for self-built executables
- You can safely click "More info" → "Run anyway"

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables as suspicious. This is a known issue:
- The executable is safe if you built it yourself from this source code
- You may need to add an exception in your antivirus software
- Consider code signing for production distribution

## Why .exe vs Python Script?

### .exe Advantages:
- No Python installation required
- Easier for non-technical users
- Single-file distribution
- Looks more "professional"

### .exe Disadvantages:
- Large file size (80-150 MB)
- Slower startup time
- Harder to modify/update
- May trigger antivirus warnings

### Python Script Advantages:
- Small file size
- Easy to modify and update
- Faster startup
- No antivirus issues
- Standard for Discord bots

**Recommendation:** Use Python script for development, .exe for distribution to non-technical users.

## Building for Different Platforms

### Windows .exe on Windows:
```cmd
build_exe.bat
```

### Linux executable on Linux:
```bash
./build_exe.sh
```

### macOS executable on macOS:
```bash
./build_exe.sh
```

**Note:** You must build on the target platform. You cannot create a Windows .exe on Linux/macOS without cross-compilation tools.

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all prerequisites are installed
3. Try rebuilding with `--clean` flag
4. Check PyInstaller documentation: https://pyinstaller.org/

---

**Happy Building!**
