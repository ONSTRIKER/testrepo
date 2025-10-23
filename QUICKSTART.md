# Quick Start Guide

Get your Discord Meeting Transcriber Bot running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install FFmpeg (choose your OS)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg
```

## Step 2: Get API Keys

1. **Discord Bot Token**
   - Go to https://discord.com/developers/applications
   - Create New Application
   - Go to "Bot" tab, click "Add Bot"
   - Enable these intents: Message Content, Server Members, Presence
   - Copy token

2. **OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy key

3. **Anthropic API Key**
   - Go to https://console.anthropic.com/
   - Generate API key
   - Copy key

## Step 3: Configure

```bash
# Copy example config
cp .env.example .env

# Edit .env and paste your keys
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```
DISCORD_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=sk-proj-your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

## Step 4: Invite Bot to Your Server

1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scope: `bot`
3. Select permissions: Send Messages, Connect, Speak, Use Voice Activity
4. Copy the generated URL
5. Open URL in browser and invite to your server

## Step 5: Run the Bot

```bash
python discord_meeting_bot.py
```

You should see:
```
Starting Discord Meeting Transcriber Bot...
YourBot#1234 has connected to Discord!
Ready to transcribe meetings!
```

## Step 6: Test It Out

In Discord:

1. Join a voice channel
2. Type: `!join`
3. Type: `!record`
4. Talk for a bit (test with friends or talk to yourself)
5. Type: `!stop`
6. Wait for transcription and summary

That's it! Check the `transcripts/` folder for your results.

## Common Issues

**Bot won't start:**
- Check all API keys are correct in `.env`
- Make sure `.env` file exists

**Bot won't join voice:**
- Verify bot has proper permissions
- Check you're in a voice channel first

**No transcription:**
- Ensure FFmpeg is installed
- Check OpenAI API has credits
- Verify audio file was created in `recordings/`

## Next Steps

- Read full README.md for advanced features
- Customize settings in `.env`
- Set up automatic startup (see README)

## Quick Command Reference

- `!join` - Bot joins voice
- `!record` - Start recording
- `!stop` - Stop and process
- `!status` - Check recording
- `!leave` - Bot leaves voice

---

**Need help?** Check the full README.md or troubleshooting section.
