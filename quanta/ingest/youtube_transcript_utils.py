import os
import subprocess
import tempfile
import traceback
import json
import shutil

from datetime import datetime as dt

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from rich.console import Console
from rich import print

import whisper

console = Console()
whisper_model = whisper.load_model("medium", compute_type="int8")


def extract_transcript(video_id: str) -> str:
    print(f"🎯 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line["text"] for line in transcript_list if "text" in line]

        if not texts:
            print("⚠️ Captions are empty — using whisper fallback.")
            raise ValueError("Empty transcript")

        print(f"📝 Captions retrieved: {len(texts)} lines")
        return "\n".join(texts)

    except (NoTranscriptFound, TranscriptsDisabled, Exception) as e:
        print(f"⚠️ Transcript API failed: {e}")
        return transcribe_audio_with_whisper(video_id)


def download_audio_clip(video_id: str) -> str:
    print(f"📥 Downloading video for Whisper: {video_id}")
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input")
        wav_path = os.path.join(tmpdir, "audio.wav")

        yt_dlp_cmd = [
            "yt-dlp", f"https://www.youtube.com/watch?v={video_id}",
            "-o", input_path,
            "--quiet", "--no-warnings",
        ]
        subprocess.run(yt_dlp_cmd, check=False)

        downloaded = next(
            (f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))),
            None
        )
        if not downloaded:
            raise FileNotFoundError("❌ yt_dlp did not produce a usable audio file.")

        input_path = os.path.join(tmpdir, downloaded)
        print(f"📂 Downloaded video: {input_path}")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", wav_path,
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"🔄 Converting video to WAV...")

        if not os.path.exists(wav_path):
            raise RuntimeError("⚠️ WAV file was not created by ffmpeg.")

        wav_size = os.path.getsize(wav_path)
        print(f"📦 WAV file size: {wav_size} bytes")
        if wav_size < 10_000:
            print("⚠️ WAV file is suspiciously small – likely no usable audio.")
            return ""

        return wav_path


def transcribe_audio_with_whisper(video_id: str) -> str:
    try:
        wav_path = download_audio_clip(video_id)
        if not wav_path:
            return ""

        print("🧠 Transcribing with Whisper...")
        segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
        print(json.dumps(segments, indent=2, ensure_ascii=False))  # Optional debug print

        if not segments or "segments" not in segments or not segments["segments"]:
            print("❌ Whisper returned no valid segments.")
            return ""

        texts = [seg["text"] for seg in segments["segments"] if "text" in seg]
        if not texts:
            print("⚠️ Whisper returned an empty transcript.")
            return ""

        print(f"✅ Transcribed {len(texts)} segments.")
        return "\n".join(texts)

    except Exception as e:
        print(f"❌ Whisper fallback failed: {e}")
        traceback.print_exc()
        return ""


def extract_transcript_fallback(video_id: str) -> str:
    return extract_transcript(video_id)


# 🔍 Optional fuzzy keyword anchor placemarks (for downstream use)
def contains_keywords(text: str) -> bool:
    patterns = [
        "breakout", "consolidation", "support", "resistance",
        "entry", "stop loss", "trigger", "crossover", "macd",
        "fibonacci", "double top", "head and shoulders"
    ]
    return any(p.lower() in text.lower() for p in patterns)


