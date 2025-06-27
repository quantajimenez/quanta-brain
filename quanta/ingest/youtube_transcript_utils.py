import os
import tempfile
import traceback
import subprocess
import json
import wave
import signal

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from rich.console import Console
import whisper

console = Console()
whisper_model = whisper.load_model("small")  # Safer for CPU environments

class TimeoutException(Exception): pass

def timeout_handler(signum, frame):
    raise TimeoutException("Whisper transcription timed out.")

def extract_transcript(video_id: str) -> str:
    console.print(f"🧠 Attempting transcript for video ID: {video_id}")

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [seg['text'] for seg in transcript_list if 'text' in seg]
        if not texts:
            console.print("⚠️ Transcript API returned empty — using Whisper fallback.")
            raise ValueError("Transcript blank")
        return "\n".join(texts)
    except (NoTranscriptFound, TranscriptsDisabled, Exception) as e:
        console.print(f"⚠️ Transcript API failed: {e}")
        return transcribe_audio_with_whisper(video_id)

def download_audio(video_id: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.webm")
        output_path = os.path.join(tmpdir, "audio.wav")

        console.print(f"📥 Downloading video for Whisper: {video_id}")
        cmd = [
            "yt-dlp",
            "-f", "bestaudio",
            f"https://www.youtube.com/watch?v={video_id}",
            "-o", input_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("❌ yt-dlp failed to download video.")

        console.print("🔄 Converting video to WAV...")
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            output_path
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("❌ ffmpeg conversion failed.")

        if not os.path.exists(output_path):
            raise RuntimeError("⚠️ WAV file was not created by ffmpeg.")

        wav_size = os.path.getsize(output_path)
        console.print(f"📦 WAV file size: {wav_size} bytes")

        try:
            with wave.open(output_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                console.print(f"📊 WAV duration: {duration:.2f} seconds")
        except:
            console.print("⚠️ Unable to measure WAV duration.")

        if wav_size < 10_000:
            console.print("⚠️ WAV file is suspiciously small — likely no usable audio.")
            return ""

        return output_path

def transcribe_audio_with_whisper(video_id: str) -> str:
    try:
        wav_path = download_audio(video_id)
        if not wav_path:
            return ""

        console.print("🧠 Transcribing with Whisper...")

        # Optional: Timeout protection
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(300)  # 5-minute timeout

        segments = whisper_model.transcribe(wav_path, beam_size=5, best_of=5)
        signal.alarm(0)

        print(json.dumps(segments, indent=2))  # Debug output

        if not segments or 'segments' not in segments:
            console.print("❌ Whisper returned no valid segments.")
            return ""

        texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
        if not texts:
            console.print("⚠️ Whisper returned an empty transcript.")
            return ""

        console.print(f"✅ Transcribed {len(texts)} segments.")
        return "\n".join(texts)

    except TimeoutException as e:
        console.print(f"❌ Transcription timeout: {e}")
        return ""
    except Exception as e:
        console.print(f"❌ Whisper fallback failed: {e}")
        traceback.print_exc()
        return ""

def extract_transcript_plain(video_id: str) -> str:
    return extract_transcript(video_id)



