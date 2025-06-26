import os
import subprocess
import tempfile
import traceback
import shutil
import json

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import whisper

whisper_model = whisper.load_model("medium")  # Adjust model if needed

def extract_transcript(video_id: str) -> str:
    print(f"🧠 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [seg["text"] for seg in transcript_list if "text" in seg]
        if not texts:
            print("⚠️ Transcript API is empty — using Whisper fallback.")
            raise ValueError("Empty transcript list.")
        return "\n".join(texts)
    except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
        print(f"⚠️ Transcript API failed: {e}")
        return transcribe_audio_with_whisper(video_id)

def download_audio(video_id: str) -> str:
    print(f"🎥 Downloading video for Whisper: {video_id}")
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, f"{video_id}.%(ext)s")
        command = [
            "yt-dlp",
            "-f", "bestaudio",
            f"https://www.youtube.com/watch?v={video_id}",
            "-o", output_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(f"❌ yt-dlp failed: {result.stderr.decode()}")
        downloaded = next((f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))), None)
        if not downloaded:
            raise RuntimeError("❌ yt-dlp did not produce a usable audio file.")
        input_path = os.path.join(tmpdir, downloaded)
        print(f"📥 Downloaded video: {input_path}")

        # Convert to wav
        wav_path = os.path.join(tmpdir, f"{video_id}.wav")
        cmd = ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(wav_path):
            raise RuntimeError("❌ WAV file was not created by ffmpeg.")
        wav_size = os.path.getsize(wav_path)
        print(f"📦 WAV file size: {wav_size} bytes")
        if wav_size < 10_000:
            print("⚠️ WAV file is suspiciously small – likely no usable audio.")
            return ""
        return wav_path

def transcribe_audio_with_whisper(video_id: str) -> str:
    try:
        print("🧠 Transcribing with Whisper...")
        wav_path = download_audio(video_id)
        if not wav_path:
            return ""

        result = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
        print("📋 Whisper output keys:", result.keys())
        print("📋 Whisper segments (raw):", json.dumps(result, indent=2, ensure_ascii=False))

        if not isinstance(result, dict) or 'segments' not in result or not result['segments']:
            print("❌ Whisper returned no valid segments.")
            return ""

        texts = [seg['text'] for seg in result['segments'] if 'text' in seg]
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
    return transcribe_audio_with_whisper(video_id)

def contains_keywords(text: str, patterns: list) -> bool:
    return any(keyword in text for keyword in patterns)

