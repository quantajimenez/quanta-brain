import os
import subprocess
import tempfile
import traceback
import json
import re
from datetime import datetime as dt

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptUnavailable, NoTranscriptFound
from rich.console import Console
from rich import print

console = Console()
whisper_model = whisper.load_model("medium", compute_type="int8")

def extract_transcript(video_id: str) -> str:
    print(f"📼 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [seg['text'] for seg in transcript_list if 'text' in seg]
        if not texts:
            print("⚠️ Transcript API empty — using Whisper fallback.")
            raise TranscriptUnavailable(video_id)
        print("📜 Captions preview:", list(texts)[:5])
        return "\n".join(texts)
    except (NoTranscriptFound, TranscriptUnavailable) as e:
        print(f"❌ Transcript API failed: {e}")
        raise e  # allow fallback

def download_audio(video_id: str, tmpdir: str) -> str:
    print(f"🔌 Downloading video for Whisper: {video_id}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmpdir, 'input.%(ext)s'),
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    input_path = next((f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))), None)
    if not input_path:
        raise FileNotFoundError("❌ yt_dlp did not produce a usable audio file.")
    input_path = os.path.join(tmpdir, input_path)
    print(f"📥 Downloaded video: {input_path}")
    return input_path

def convert_to_wav(input_path: str, tmpdir: str) -> str:
    wav_path = os.path.join(tmpdir, "converted.wav")
    print("🔄 Converting video to WAV...")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError("❌ ffmpeg conversion failed.")
    if not os.path.exists(wav_path):
        raise RuntimeError("⚠️ WAV file was not created by ffmpeg.")
    wav_size = os.path.getsize(wav_path)
    print(f"📏 WAV file size: {wav_size} bytes")
    if wav_size < 10_000:
        print("⚠️ WAV file is suspiciously small — likely no usable audio.")
        return ""
    return wav_path

def transcribe_audio_with_whisper(video_id: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            input_path = download_audio(video_id, tmpdir)
            wav_path = convert_to_wav(input_path, tmpdir)
            if not wav_path:
                return ""
            print("🧠 Transcribing with Whisper...")
            segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
            print(json.dumps(segments, indent=2, ensure_ascii=False))  # full debug
            if not segments or 'segments' not in segments or not segments['segments']:
                print("❌ Whisper returned no valid segments.")
                return ""
            texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
            if not texts:
                print("⚠️ Whisper returned an empty transcript.")
                return ""
            print(f"✅ Transcribed {len(texts)} segments.")
            print("\n".join(texts[:5]))  # optional preview
            return "\n".join(texts)
        except Exception as e:
            print(f"❌ Whisper fallback failed: {e}")
            traceback.print_exc()
            return ""

def extract_transcript_fallback(video_id: str) -> str:
    try:
        return extract_transcript(video_id)
    except:
        return transcribe_audio_with_whisper(video_id)

# 🔍 Optional fuzzy keyword matcher placeholder for downstream use:
def contains_pattern(text: str) -> bool:
    text = text.lower()
    patterns = [
        ("macd", "crossover"),
        ("rsi", "oversold"),
        ("bollinger", "break"),
        ("moving average", "cross"),
        ("head", "shoulders"),
    ]
    return any(all(keyword in text for keyword in pattern) for pattern in patterns)


