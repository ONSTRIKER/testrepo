import discord
from discord.ext import commands
import asyncio
import os
import wave
import datetime
from pathlib import Path
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import json

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
MAX_RECORDING_DURATION = int(os.getenv('MAX_RECORDING_DURATION', 3600))
RECORDINGS_DIR = Path(os.getenv('RECORDINGS_DIR', './recordings'))
TRANSCRIPTS_DIR = Path(os.getenv('TRANSCRIPTS_DIR', './transcripts'))

# Create directories if they don't exist
RECORDINGS_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

# Initialize APIs
openai.api_key = OPENAI_API_KEY
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store active recordings
active_recordings = {}


class AudioSink(discord.sinks.WaveSink):
    """Custom audio sink to record voice channel audio"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_data = {}

    def write(self, data, user):
        """Write audio data for each user"""
        if user not in self.audio_data:
            self.audio_data[user] = []
        self.audio_data[user].append(data)


async def transcribe_audio(audio_file_path):
    """Transcribe audio using OpenAI Whisper"""
    try:
        print(f"Transcribing audio file: {audio_file_path}")

        with open(audio_file_path, 'rb') as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )

        return transcript
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


async def summarize_with_claude(transcript_text, meeting_info):
    """Generate summary and notes using Claude"""
    try:
        print("Generating summary with Claude...")

        prompt = f"""You are analyzing a Discord voice meeting transcript. Please provide:

1. A concise summary of the meeting (2-3 paragraphs)
2. Key discussion points (bullet points)
3. Action items or decisions made (if any)
4. Important topics covered
5. Notable participants and their contributions

Meeting Information:
- Date: {meeting_info['date']}
- Duration: {meeting_info['duration']}
- Channel: {meeting_info['channel']}
- Participants: {', '.join(meeting_info['participants'])}

Transcript:
{transcript_text}

Please format your response in a clear, organized manner."""

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text
    except Exception as e:
        print(f"Error summarizing with Claude: {e}")
        return None


@bot.event
async def on_ready():
    """Event handler for when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print('Ready to transcribe meetings!')


@bot.command(name='join', help='Join your current voice channel')
async def join(ctx):
    """Join the voice channel of the command author"""
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel first!")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"Moved to {channel.name}")
    else:
        await channel.connect()
        await ctx.send(f"Joined {channel.name}")


@bot.command(name='leave', help='Leave the current voice channel')
async def leave(ctx):
    """Disconnect from voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel")
    else:
        await ctx.send("I'm not in a voice channel!")


@bot.command(name='record', help='Start recording the meeting')
async def start_recording(ctx):
    """Start recording the voice channel"""
    if not ctx.voice_client:
        await ctx.send("I need to join a voice channel first! Use !join")
        return

    if ctx.guild.id in active_recordings:
        await ctx.send("Already recording in this server!")
        return

    voice_client = ctx.voice_client

    # Create recording session info
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    recording_info = {
        'session_id': session_id,
        'channel': ctx.channel.name,
        'voice_channel': voice_client.channel.name,
        'start_time': datetime.datetime.now(),
        'participants': [member.name for member in voice_client.channel.members if not member.bot]
    }

    active_recordings[ctx.guild.id] = recording_info

    # Start recording
    sink = AudioSink()

    async def finished_callback(sink, channel, *args):
        """Called when recording is finished"""
        await process_recording(sink, recording_info, channel)

    voice_client.start_recording(
        sink,
        finished_callback,
        ctx.channel
    )

    await ctx.send(f"Recording started! Session ID: {session_id}")
    await ctx.send("Use !stop to end the recording and generate transcript.")


@bot.command(name='stop', help='Stop recording and generate transcript')
async def stop_recording(ctx):
    """Stop recording and process the audio"""
    if ctx.guild.id not in active_recordings:
        await ctx.send("No active recording in this server!")
        return

    if not ctx.voice_client or not ctx.voice_client.recording:
        await ctx.send("Not currently recording!")
        return

    await ctx.send("Stopping recording... This may take a moment.")
    ctx.voice_client.stop_recording()


async def process_recording(sink, recording_info, channel):
    """Process the recorded audio: save, transcribe, and summarize"""
    try:
        session_id = recording_info['session_id']
        end_time = datetime.datetime.now()
        duration = (end_time - recording_info['start_time']).total_seconds()

        await channel.send("Processing recording...")

        # Save audio files
        recorded_users = [user for user in sink.audio_data.keys()]
        audio_files = []

        for user, audio in sink.audio_data.items():
            filename = f"{session_id}_{user.name}.wav"
            filepath = RECORDINGS_DIR / filename

            # Save the audio file
            with wave.open(str(filepath), 'wb') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(48000)
                for data in audio:
                    wav_file.writeframes(data)

            audio_files.append(filepath)
            print(f"Saved audio for {user.name}: {filepath}")

        await channel.send(f"Saved {len(audio_files)} audio files. Starting transcription...")

        # Transcribe each audio file
        all_transcripts = []

        for audio_file in audio_files:
            transcript = await transcribe_audio(audio_file)
            if transcript:
                user_name = audio_file.stem.split('_', 1)[1]
                all_transcripts.append({
                    'user': user_name,
                    'text': transcript.text,
                    'segments': getattr(transcript, 'segments', [])
                })

        if not all_transcripts:
            await channel.send("Failed to transcribe audio.")
            return

        # Combine transcripts
        combined_transcript = "\n\n".join([
            f"[{t['user']}]: {t['text']}" for t in all_transcripts
        ])

        await channel.send("Transcription complete! Generating summary with Claude...")

        # Generate summary with Claude
        meeting_info = {
            'date': recording_info['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
            'duration': f"{int(duration // 60)} minutes {int(duration % 60)} seconds",
            'channel': recording_info['voice_channel'],
            'participants': recording_info['participants']
        }

        summary = await summarize_with_claude(combined_transcript, meeting_info)

        # Save transcript and summary
        transcript_file = TRANSCRIPTS_DIR / f"{session_id}_transcript.txt"
        summary_file = TRANSCRIPTS_DIR / f"{session_id}_summary.txt"
        full_report_file = TRANSCRIPTS_DIR / f"{session_id}_full_report.md"

        # Save transcript
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write("MEETING TRANSCRIPT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {meeting_info['date']}\n")
            f.write(f"Duration: {meeting_info['duration']}\n")
            f.write(f"Channel: {meeting_info['channel']}\n")
            f.write(f"Participants: {', '.join(meeting_info['participants'])}\n\n")
            f.write("=" * 50 + "\n\n")
            f.write(combined_transcript)

        # Save summary
        if summary:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)

        # Save full report
        with open(full_report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Meeting Report - {session_id}\n\n")
            f.write(f"**Date:** {meeting_info['date']}\n")
            f.write(f"**Duration:** {meeting_info['duration']}\n")
            f.write(f"**Channel:** {meeting_info['channel']}\n")
            f.write(f"**Participants:** {', '.join(meeting_info['participants'])}\n\n")
            f.write("---\n\n")
            if summary:
                f.write("## Summary & Notes\n\n")
                f.write(summary)
                f.write("\n\n---\n\n")
            f.write("## Full Transcript\n\n")
            f.write(combined_transcript)

        # Send completion message
        await channel.send("Meeting processing complete!")
        await channel.send(f"Files saved:\n- Transcript: `{transcript_file.name}`\n- Summary: `{summary_file.name}`\n- Full Report: `{full_report_file.name}`")

        # Send summary preview
        if summary:
            # Split summary into chunks if too long
            max_length = 1900
            if len(summary) <= max_length:
                await channel.send(f"**Summary:**\n{summary}")
            else:
                await channel.send(f"**Summary (preview):**\n{summary[:max_length]}...\n\n*Full summary saved to file*")

    except Exception as e:
        print(f"Error processing recording: {e}")
        await channel.send(f"Error processing recording: {str(e)}")
    finally:
        # Clean up active recording
        guild_id = None
        for gid, info in active_recordings.items():
            if info['session_id'] == recording_info['session_id']:
                guild_id = gid
                break
        if guild_id:
            del active_recordings[guild_id]


@bot.command(name='status', help='Check recording status')
async def status(ctx):
    """Check if recording is active"""
    if ctx.guild.id in active_recordings:
        info = active_recordings[ctx.guild.id]
        duration = (datetime.datetime.now() - info['start_time']).total_seconds()
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        await ctx.send(f"Recording in progress!\n"
                      f"Session ID: {info['session_id']}\n"
                      f"Duration: {minutes}m {seconds}s\n"
                      f"Participants: {', '.join(info['participants'])}")
    else:
        await ctx.send("No active recording. Use !record to start!")


@bot.command(name='help_meeting', help='Show all available commands')
async def help_meeting(ctx):
    """Display help information"""
    help_text = """
**Discord Meeting Transcriber Bot**

**Commands:**
`!join` - Join your current voice channel
`!leave` - Leave the voice channel
`!record` - Start recording the meeting
`!stop` - Stop recording and generate transcript + summary
`!status` - Check current recording status
`!help_meeting` - Show this help message

**How to use:**
1. Join a voice channel
2. Type `!join` to make the bot join
3. Type `!record` to start recording
4. Have your meeting
5. Type `!stop` to end recording and get transcript + AI summary

**Features:**
- Automatic transcription using Whisper AI
- Intelligent summaries and notes using Claude
- Saves audio files, transcripts, and summaries
- Identifies speakers and timestamps
    """
    await ctx.send(help_text)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param}")
    else:
        await ctx.send(f"An error occurred: {str(error)}")
        print(f"Error: {error}")


def main():
    """Main function to run the bot"""
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file based on .env.example")
        return

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found in environment variables!")
        return

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables!")
        return

    print("Starting Discord Meeting Transcriber Bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
