import os
import subprocess
import tempfile
import traceback
import json
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from rich.console import Console
from rich import print
import whisper

console = Console()
whisper_model = whisper.load_model("medium")  # Removed unsupported 'compute_type' argument


def extract_transcript(video_id: str) -> str:
    console.print(f"🧠 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line['text'] for line in transcript_list if 'text' in line]

        if not texts:
            print("⚠️ Captions API empty — using whisper fallback.")
            return transcribe_audio_with_whisper(video_id)

        return "\n".join(texts)

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        print(f"⚠️ Transcript API failed: {e}")
        return transcribe_audio_with_whisper(video_id)
    except Exception as e:
        print(f"❌ Transcript API unknown failure: {e}")
        traceback.print_exc()
        return transcribe_audio_with_whisper(video_id)


def download_audio(video_id: str) -> str:
    console.print(f"📥 Downloading video for Whisper: {video_id}")
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "input.%(ext)s")
        command = [
            "yt-dlp",
            f"https://www.youtube.com/watch?v={video_id}",
            "-f", "bestaudio",
            "-o", output_path,
        ]

        result = subprocess.run(command, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("❌ yt-dlp download failed.")

        # Get downloaded webm or mp4 file
        input_path = None
        for f in os.listdir(tmpdir):
            if f.endswith((".mp4", ".webm", ".mkv")):
                input_path = os.path.join(tmpdir, f)
                break

        if not input_path:
            raise FileNotFoundError("❌ yt-dlp did not produce a usable audio file.")

        wav_path = os.path.join(tmpdir, "audio.wav")
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            wav_path,
        ]

        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
        wav_path = download_audio(video_id)
        if not wav_path:
            return ""

        console.print("🧠 Transcribing with Whisper...")

        segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)

        print(json.dumps(segments, indent=2))  # Optional debug print

        if not segments or 'segments' not in segments:
            console.print("❌ Whisper returned no valid segments.")
            return ""

        texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
        if not texts:
            console.print("⚠️ Whisper returned an empty transcript.")
            return ""

        console.print(f"✅ Transcribed {len(texts)} segments.")
        return "\n".join(texts)

    except Exception as e:
        console.print(f"❌ Whisper fallback failed: {e}")
        traceback.print_exc()
        return ""



