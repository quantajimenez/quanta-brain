import os
import tempfile
import traceback
import subprocess
import json
import time

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from rich.console import Console
from rich import print

import whisper

console = Console()
whisper_model = whisper.load_model("medium")  # Removed compute_type for compatibility

def extract_transcript(video_id: str) -> str:
    print(f"🧠 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [seg["text"] for seg in transcript_list if "text" in seg]
        if not texts:
            print("⚠️ Transcript API is empty – using whisper fallback.")
            raise ValueError("Empty transcript")
        print(f"📜 Transcript API returned {len(texts)} segments.")
        return "\n".join(texts)
    except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
        print(f"⚠️ Transcript API failed: {e}")
        return ""  # Fall back to Whisper


def download_video(video_id: str, output_path: str) -> str:
    print(f"📥 Downloading video for Whisper: {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = output_path.replace(".mp4", "")  # yt_dlp adds extension
    command = ["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "webm", "-o", f"{output_path}.%(ext)s", url]
    subprocess.run(command, check=True)
    downloaded = next((f for f in os.listdir(os.path.dirname(output_path)) if f.startswith(os.path.basename(output_path)) and f.endswith((".mp4", ".webm", ".mkv"))), None)
    if not downloaded:
        raise FileNotFoundError(f"❌ yt_dlp did not produce a usable audio file.")
    path = os.path.join(os.path.dirname(output_path), downloaded)
    print(f"📁 Downloaded video: {path}")
    return path


def transcribe_audio_with_whisper(video_id: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = download_video(video_id, os.path.join(tmpdir, "input"))
        wav_path = os.path.join(tmpdir, "audio.wav")

        # Convert to WAV
        print("🔄 Converting video to WAV...")
        result = subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print(f"❌ ffmpeg conversion failed.\n{result.stderr.decode()}")
            raise RuntimeError("❌ ffmpeg conversion failed.")

        if not os.path.exists(wav_path):
            raise RuntimeError("⚠️ WAV file was not created by ffmpeg.")

        wav_size = os.path.getsize(wav_path)
        print(f"📦 WAV file size: {wav_size} bytes")
        if wav_size < 10_000:
            print("⚠️ WAV file is suspiciously small – likely no usable audio.")
            return ""

        # Transcribe with Whisper
        try:
            print("🧠 Transcribing with Whisper...")
            segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
            print(json.dumps(segments, indent=2, ensure_ascii=False))  # Optional debug print

            if not segments or 'segments' not in segments:
                print("❌ Whisper returned no valid segments.")
                return ""

            texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
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
    transcript = extract_transcript(video_id)
    if not transcript:
        transcript = transcribe_audio_with_whisper(video_id)
    return transcript


def apply_patterns(text: str, patterns: list) -> bool:
    if not text or not patterns:
        return False
    return any(keyword.lower() in text.lower() for keyword in patterns)



