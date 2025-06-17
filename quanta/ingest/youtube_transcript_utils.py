import os
import json
import traceback
import tempfile
import subprocess
import yt_dlp
import xml.etree.ElementTree as ET

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.error import HTTPError
from faster_whisper import WhisperModel

whisper_model = WhisperModel("medium", compute_type="int8")


def extract_transcript(video_id: str) -> str:
    print(f"\n🎬 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line['text'] for line in transcript_list if 'text' in line]

        if not texts:
            print("⚠️ Captions are empty — using Whisper fallback.")
            return transcribe_audio_with_whisper(video_id)

        print(f"✅ Captions retrieved: {len(texts)} lines")
        return "\n".join(texts)

    except (NoTranscriptFound, TranscriptsDisabled, HTTPError) as e:
        print(f"🟠 Transcript unavailable: {type(e).__name__} – {e}")
        return transcribe_audio_with_whisper(video_id)

    except ET.ParseError as e:
        print(f"❌ Transcript API returned malformed XML: {e}")
        return transcribe_audio_with_whisper(video_id)

    except Exception as e:
        print(f"❌ Unhandled error in transcript extraction: {e}")
        traceback.print_exc()
        return transcribe_audio_with_whisper(video_id)


def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🛠️ Whisper fallback engaged via yt_dlp...")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"🔗 Downloading from: {video_url}")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "input.%(ext)s")
            wav_path = os.path.join(tmpdir, "converted.wav")

            # Download audio
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "merge_output_format": "mp4",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Accept any audio container format
            downloaded = next((f for f in os.listdir(tmpdir) if f.endswith((".mp4", ".webm", ".mkv"))), None)

            if not downloaded:
                raise FileNotFoundError("❌ yt_dlp did not produce a usable audio file.")

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
            if not os.path.exists(wav_path):
                raise RuntimeError("⚠️ WAV file was not created by ffmpeg.")

            wav_size = os.path.getsize(wav_path)
            print(f"📦 WAV file size: {wav_size} bytes")
            if wav_size < 10_000:
                print("⚠️ WAV file is suspiciously small — likely no usable audio.")
                return ""

            # Transcribe with Whisper
            try:
                print("🧠 Transcribing with Whisper...")
                segments = list(whisper_model.transcribe(wav_path, beam_size=5, best_of=5))
                serializable_segments = []
                for seg in segments:
                    if hasattr(seg, "_asdict"):
                        serializable_segments.append(seg._asdict())
                    elif isinstance(seg, dict):
                        serializable_segments.append(seg)
                    else:
                        serializable_segments.append({"text": str(seg)})
                
                print(json.dumps(serializable_segments, indent=2, ensure_ascii=False))



                if not segments:
                    print("❌ Whisper returned no valid segments.")
                    return ""

                texts = [seg['text'] for seg in segments if 'text' in seg]
                if not texts:
                    print("⚠️ Whisper returned an empty transcript.")
                    return ""

                print(f"✅ Transcribed {len(texts)} segments.")
                return "\n".join(texts)

            except Exception as e:
                print(f"❌ Whisper fallback failed: {e}")
                traceback.print_exc()
                return ""

    except Exception as e:
        print(f"❌ Whisper processing failed: {e}")
        traceback.print_exc()
        return ""

