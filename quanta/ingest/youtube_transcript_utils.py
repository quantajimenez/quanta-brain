import os
import json
import shutil
import traceback
import subprocess
from tempfile import TemporaryDirectory
from yt_dlp import YoutubeDL

from youtube_transcript_api import YouTubeTranscriptApi
from faster_whisper import WhisperModel
from rich import print

whisper_model = WhisperModel("medium", compute_type="int8")

def extract_transcript(video_id: str) -> str:
    print(f"📄 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line["text"] for line in transcript_list if "text" in line]
        if not texts:
            print("⚠️ Captions are empty — using Whisper fallback.")
            return transcribe_audio_with_whisper(video_id)
        print("🟢 Captions retrieved.")
        return "\n".join(texts)
    except Exception as e:
        print(f"⚠️ Transcript API failed: ({e})")
        return transcribe_audio_with_whisper(video_id)

def transcribe_audio_with_whisper(video_id: str) -> str:
    try:
        with TemporaryDirectory() as tmpdir:
            print(f"📥 Downloading video for Whisper: {video_id}")
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(tmpdir, "input.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "extractaudio": True,
                "audioformat": "wav"
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

            downloaded = next((f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))), None)
            if not downloaded:
                raise FileNotFoundError("❌ yt_dlp did not produce a usable audio file.")

            input_path = os.path.join(tmpdir, downloaded)
            print(f"📦 Downloaded video: {input_path}")

            # Convert to WAV
            wav_path = os.path.join(tmpdir, "output.wav")
            print("🔄 Converting video to WAV...")
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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

            # Transcribe
            print("🧠 Transcribing with Whisper...")
            segments_raw = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
            segments_raw = list(segments_raw)

            serializable_segments = []
            for s in segments_raw:
                if hasattr(s, "_asdict"):
                    serializable_segments.append(s._asdict())
                elif isinstance(s, dict):
                    serializable_segments.append(s)
                else:
                    serializable_segments.append({"text": str(s)})

            print(json.dumps(serializable_segments, indent=2, ensure_ascii=False))  # Optional debug print

            if not serializable_segments:
                print("❌ Whisper returned no valid segments.")
                return ""

            texts = [seg["text"] for seg in serializable_segments if "text" in seg]
            if not texts:
                print("⚠️ Whisper returned an empty transcript.")
                return ""

            print(f"✅ Transcribed {len(texts)} segments.")
            return "\n".join(texts)

    except Exception as e:
        print(f"❌ Whisper fallback failed: ({e})")
        traceback.print_exc()
        return ""

