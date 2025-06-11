# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import tempfile
import subprocess
import os
from pytube import YouTube
from faster_whisper import WhisperModel

# Load Whisper model once
whisper_model = WhisperModel("base", compute_type="int8")  # Or float16 for GPU

def extract_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([line['text'] for line in transcript_list])
        if not transcript_text.strip():
            raise ValueError("Transcript from YouTube API is empty.")
        return transcript_text
    except (NoTranscriptFound, TranscriptsDisabled, ValueError) as e:
        print(f"⚠️ Fallback to Whisper for video {video_id}: {e}")
        return transcribe_audio_with_whisper(video_id)
    except Exception as e:
        print(f"❌ Unexpected error for video {video_id}: {e}")
        return ""

def transcribe_audio_with_whisper(video_id: str) -> str:
    print(f"🔁 No captions found — falling back to faster-Whisper STT for {video_id}")

    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(yt_url)
    stream = yt.streams.filter(only_audio=True).first()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input_audio.mp4")
        output_path = os.path.join(tmpdir, "converted_audio.wav")
        stream.download(filename=input_path)

        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1",  # Mono 16kHz
            output_path
        ], check=True)

        try:
            segments, _ = whisper_model.transcribe(output_path)
            return "\n".join([segment.text for segment in segments]) if segments else ""
        except Exception as e:
            print(f"❌ Whisper transcription failed: {e}")
            return ""
