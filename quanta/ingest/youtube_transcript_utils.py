import os
import re
import json
import shutil
import logging
import tempfile
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import whisper

logger = logging.getLogger("youtubeTranscriptUtils")
whisper_model = whisper.load_model("medium")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?%]", "", text)
    return text.strip()

def extract_transcript(video_id):
    logger.info(f"🧠 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line["text"] for line in transcript_list if "text" in line]
        if not texts:
            logger.warning("📜 Captions are empty – using Whisper fallback.")
            return transcribe_audio_with_whisper(video_id)
        return "\n".join(texts)
    except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
        logger.warning(f"📜 Transcript API failed: {e}")
        return transcribe_audio_with_whisper(video_id)

def download_audio_clip(video_id, tmpdir):
    logger.info(f"📥 Downloading video for Whisper: {video_id}")
    input_path = os.path.join(tmpdir, "input.webm")
    output_path = os.path.join(tmpdir, "audio.wav")

    ydl_opts = {
        'outtmpl': os.path.join(tmpdir, "input.%(ext)s"),
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

    # Identify the downloaded file
    downloaded = next((f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))), None)
    if not downloaded:
        raise RuntimeError(f"❌ yt_dlp did not produce a usable audio file.")

    input_path = os.path.join(tmpdir, downloaded)
    logger.info(f"📼 Downloaded video: {input_path}")

    # Convert to WAV
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-f", "wav", "-ar", "16000", "-ac", "1", output_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    if result.returncode != 0 or not os.path.exists(output_path):
        raise RuntimeError("❌ ffmpeg conversion failed or WAV file missing.")

    wav_size = os.path.getsize(output_path)
    logger.info(f"📏 WAV file size: {wav_size} bytes")
    if wav_size < 100_000:
        logger.warning("⚠️ WAV file is suspiciously small – likely no usable audio.")
        return None

    return output_path

def transcribe_audio_with_whisper(video_id):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = download_audio_clip(video_id, tmpdir)
            if not wav_path:
                return ""

            logger.info("🧠 Transcribing with Whisper...")
            segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)

            if not segments or "segments" not in segments:
                logger.warning("❌ Whisper returned no valid segments.")
                return ""

            texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
            if not texts:
                logger.warning("⚠️ Whisper returned an empty transcript.")
                return ""

            logger.info(f"✅ Transcribed {len(texts)} segments.")
            return "\n".join(texts)

    except Exception as e:
        logger.warning(f"❌ Whisper fallback failed: {e}")
        with open("failed_transcripts.log", "a") as f:
            f.write(f"{video_id}\n")
        return ""

def extract_insights(cleaned_text, patterns):
    cleaned = clean_text(cleaned_text)
    found = [p for p in patterns if p in cleaned]
    return found



