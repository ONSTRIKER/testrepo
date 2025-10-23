# Discord Meeting Transcriber Bot

An automated Discord bot that records voice meetings, transcribes them using OpenAI Whisper, and generates intelligent summaries and notes using Claude AI.

## Features

- **Automatic Voice Recording**: Records Discord voice channel conversations
- **AI Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **Intelligent Summaries**: Claude AI generates meeting summaries, key points, and action items
- **Multi-Speaker Support**: Identifies and separates different speakers
- **Easy Commands**: Simple Discord commands to control the bot
- **Organized Output**: Saves audio files, transcripts, and summaries in organized folders

## Two Ways to Use This Bot

### Option 1: Windows Executable (.exe) - Easiest!

**Best for:** Non-technical users who just want to run the bot.

- No Python installation required
- Double-click to run
- See **[BUILD_EXE.md](BUILD_EXE.md)** for complete instructions

**Quick Start:**
1. Download/build `DiscordMeetingTranscriber.exe`
2. Create `.env` file with API keys
3. Install FFmpeg
4. Run the .exe

### Option 2: Python Script - Most Flexible

**Best for:** Developers or those who want to customize the bot.

- Requires Python installation
- Easy to modify and update
- Standard Discord bot deployment
- Follow the instructions below

---

## Prerequisites (For Python Script Option)

1. **Python 3.8+** installed on your system
2. **Discord Bot Token** - [Create a bot on Discord Developer Portal](https://discord.com/developers/applications)
3. **OpenAI API Key** - [Get from OpenAI Platform](https://platform.openai.com/api-keys)
4. **Anthropic API Key** - [Get from Anthropic Console](https://console.anthropic.com/)
5. **FFmpeg** - Required for audio processing

### Installing FFmpeg

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**On macOS:**
```bash
brew install ffmpeg
```

**On Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Installation (Python Script)

> **Want the .exe version instead?** See **[BUILD_EXE.md](BUILD_EXE.md)**

### 1. Clone the Repository

```bash
git clone https://github.com/ONSTRIKER/testrepo.git
cd testrepo
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Copy the bot token
6. Go to "OAuth2" > "URL Generator"
7. Select scopes: `bot`
8. Select permissions:
   - Send Messages
   - Connect
   - Speak
   - Use Voice Activity
9. Copy the generated URL and invite the bot to your server

### 4. Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

### Starting the Bot

```bash
python discord_meeting_bot.py
```

You should see:
```
Starting Discord Meeting Transcriber Bot...
<BotName> has connected to Discord!
Ready to transcribe meetings!
```

### Bot Commands

All commands use the `!` prefix:

| Command | Description |
|---------|-------------|
| `!join` | Bot joins your current voice channel |
| `!leave` | Bot leaves the voice channel |
| `!record` | Start recording the meeting |
| `!stop` | Stop recording and generate transcript + summary |
| `!status` | Check current recording status |
| `!help_meeting` | Show all available commands |

### Typical Workflow

1. **Join a voice channel** in Discord
2. **Type `!join`** in a text channel to make the bot join
3. **Type `!record`** to start recording the meeting
4. **Have your meeting** - the bot records everything
5. **Type `!stop`** when done - the bot will:
   - Save all audio files
   - Transcribe using Whisper AI
   - Generate summary using Claude
   - Post results in the text channel

### Example Session

```
User: !join
Bot: Joined General Voice Channel

User: !record
Bot: Recording started! Session ID: 20241023_143022
Bot: Use !stop to end the recording and generate transcript.

[Meeting happens...]

User: !stop
Bot: Stopping recording... This may take a moment.
Bot: Processing recording...
Bot: Saved 3 audio files. Starting transcription...
Bot: Transcription complete! Generating summary with Claude...
Bot: Meeting processing complete!
Bot: Files saved:
     - Transcript: 20241023_143022_transcript.txt
     - Summary: 20241023_143022_summary.txt
     - Full Report: 20241023_143022_full_report.md
Bot: **Summary:**
     [AI-generated meeting summary appears here]
```

## Output Files

All files are saved in organized directories:

### `/recordings/` Directory
- Contains raw audio files (WAV format)
- One file per participant
- Filename format: `{session_id}_{username}.wav`

### `/transcripts/` Directory
- **`{session_id}_transcript.txt`**: Full text transcript with speaker identification
- **`{session_id}_summary.txt`**: Claude AI-generated summary and notes
- **`{session_id}_full_report.md`**: Complete markdown report with metadata, summary, and transcript

## What Claude AI Provides

The Claude AI summary includes:

1. **Concise Summary**: 2-3 paragraph overview of the meeting
2. **Key Discussion Points**: Bullet-pointed main topics
3. **Action Items**: Decisions made and tasks assigned
4. **Important Topics**: Highlighted subjects covered
5. **Participant Contributions**: Notable input from participants

## Configuration Options

Edit `.env` file to customize:

```env
# Maximum recording duration in seconds (default: 3600 = 1 hour)
MAX_RECORDING_DURATION=3600

# Directory for audio recordings
RECORDINGS_DIR=./recordings

# Directory for transcripts and summaries
TRANSCRIPTS_DIR=./transcripts
```

## Troubleshooting

### Bot doesn't join voice channel
- Ensure the bot has "Connect" and "Speak" permissions
- Check that you're in a voice channel when using `!join`

### Recording fails
- Install FFmpeg if not already installed
- Check bot permissions in Discord server settings
- Ensure sufficient disk space for recordings

### Transcription errors
- Verify OpenAI API key is valid and has credits
- Check audio file was created in `/recordings/` directory
- Ensure audio quality is sufficient (background noise may affect accuracy)

### Summary generation fails
- Verify Anthropic API key is valid
- Check API rate limits
- Ensure transcript was generated successfully

### "Missing dependencies" error
```bash
pip install -r requirements.txt --upgrade
```

### Bot disconnects during recording
- Check network connection
- Verify Discord API status
- Increase `MAX_RECORDING_DURATION` if needed

## API Costs

Be aware of API usage costs:

- **OpenAI Whisper**: ~$0.006 per minute of audio
- **Anthropic Claude**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens

A typical 1-hour meeting might cost:
- Transcription: ~$0.36
- Summary: ~$0.05-0.15
- **Total: ~$0.41-0.51**

## Privacy & Security

- All recordings are stored locally
- Transcripts are sent to OpenAI and Anthropic for processing
- Never commit `.env` file to version control
- Delete recordings when no longer needed
- Be aware of privacy laws regarding voice recording in your jurisdiction

## Advanced Usage

### Run as Background Service (Linux)

Create systemd service file `/etc/systemd/system/discord-transcriber.service`:

```ini
[Unit]
Description=Discord Meeting Transcriber Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/testrepo
ExecStart=/usr/bin/python3 discord_meeting_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-transcriber
sudo systemctl start discord-transcriber
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **Discord.py** - Discord API wrapper
- **OpenAI Whisper** - Speech recognition
- **Anthropic Claude** - AI summarization
- **FFmpeg** - Audio processing

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Discord.py documentation
3. Check API status pages for OpenAI and Anthropic

---

**Happy Meeting Transcribing!**
