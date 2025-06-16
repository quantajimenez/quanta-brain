# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import tempfile
import subprocess
import os
import traceback
from pytube import YouTube
from faster_whisper import WhisperModel

whisper_model = WhisperModel("medium", compute_type="int8")


def extract_transcript(video_id: str) -> str:
    print(f"📼 Attempting transcript for video ID: {video_id}")
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        texts = [line['text'] for line in transcript_list if 'text' in line]
        if not texts:
            print("⚠️ YouTube captions were empty, using Whisper fallback.")
            return transcribe_audio_with_whisper(video_id)

        print(f"✅ Captions retrieved: {len(texts)} lines")
        return "\n".join(texts)

    except (NoTranscriptFound, TranscriptsDisabled):
        print("🟠 No captions found — falling back to Whisper STT.")
        return transcribe_audio_with_whisper(video_id)

    except Exception as e:
        print(f"❌ Error during YouTubeTranscriptApi.get_transcript: {e}")
        traceback.print_exc()
        print("🟠 Falling back to Whisper STT.")
        return transcribe_audio_with_whisper(video_id)


def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🛠️ Using Whisper fallback...")

    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        yt = YouTube(yt_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            raise Exception("❌ No downloadable video stream found.")
    except Exception as e:
        print(f"❌ Failed to load YouTube video: {e}")
        traceback.print_exc()
        return ""

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "converted.wav")

        try:
            print(f"⬇️ Downloading stream: {stream.default_filename}")
            stream.download(filename=input_path)

            if not os.path.exists(input_path):
                raise Exception("❌ Video file not downloaded.")
            print(f"📥 Video size: {os.path.getsize(input_path)} bytes")

            print("🔄 Converting video to WAV format...")
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                print("❌ ffmpeg conversion failed:")
                print(result.stderr.decode())
                return ""

            print(f"📤 WAV file size: {os.path.getsize(output_path)} bytes")
        except Exception as e:
            print(f"❌ Error during audio processing: {e}")
            traceback.print_exc()
            return ""

        try:
            print("🧠 Transcribing audio with Whisper...")
            segments = whisper_model.transcribe(output_path)

            if not isinstance(segments, dict) or 'segments' not in segments or not segments['segments']:
                print("❌ Whisper returned no valid transcription segments.")
                return ""

            texts = [seg['text'] for seg in segments['segments'] if 'text' in seg]
            if not texts:
                print("⚠️ Whisper returned empty transcript.")
                return ""

            print(f"✅ Transcribed {len(texts)} segments.")
            return "\n".join(texts)

        except Exception as e:
            print(f"❌ Whisper transcription failed: {e}")
            traceback.print_exc()
            return ""

