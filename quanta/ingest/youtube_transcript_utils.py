# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.error import HTTPError
import tempfile
import subprocess
import os
import traceback
from pytube import YouTube
from faster_whisper import WhisperModel

whisper_model = WhisperModel("medium", compute_type="int8")


from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.error import HTTPError
import traceback
import xml.etree.ElementTree as ET

def extract_transcript(video_id: str) -> str:
    print(f"\n📼 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line['text'] for line in transcript_list if 'text' in line]

        if not texts:
            print("⚠️ Captions are empty — using Whisper fallback.")
            return transcribe_audio_with_whisper(video_id)

        print(f"✅ Captions retrieved: {len(texts)} lines")
        return "\n".join(texts)

    except (NoTranscriptFound, TranscriptsDisabled, HTTPError) as e:
        print(f"🟠 No transcript available: {type(e).__name__} – {e}")
        return transcribe_audio_with_whisper(video_id)

    except ET.ParseError as e:
        print(f"❌ Transcript API returned malformed XML: {e}")
        return transcribe_audio_with_whisper(video_id)

    except Exception as e:
        print(f"❌ Unhandled error in transcript extraction: {e}")
        traceback.print_exc()
        return transcribe_audio_with_whisper(video_id)




import yt_dlp
import tempfile
import subprocess
import os
import traceback
from faster_whisper import WhisperModel

whisper_model = WhisperModel("medium", compute_type="int8")

def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🛠️ Whisper fallback engaged via yt_dlp...")

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"🎥 Downloading from: {video_url}")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "input.%(ext)s")
            final_mp4 = os.path.join(tmpdir, "input.mp4")
            wav_path = os.path.join(tmpdir, "converted.wav")

            # Download video
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": output_path,
                "merge_output_format": "mp4",
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Ensure file exists
            downloaded = next((f for f in os.listdir(tmpdir) if f.endswith(".mp4")), None)
            if not downloaded:
                raise FileNotFoundError("❌ yt_dlp did not download a valid .mp4 file.")

            input_path = os.path.join(tmpdir, downloaded)
            print(f"📥 Downloaded video: {input_path}")

            # Convert to WAV
            print("🎛️ Converting video to WAV...")
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                raise RuntimeError("❌ ffmpeg conversion failed.")

            print("🧠 Transcribing with Whisper...")
            segments = whisper_model.transcribe(wav_path)

            if not isinstance(segments, dict) or 'segments' not in segments or not segments['segments']:
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

