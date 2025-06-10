# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import tempfile
import subprocess
import os
import whisper
from pytube import YouTube

# Load Whisper model once at module level
whisper_model = whisper.load_model("base")


def extract_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([line['text'] for line in transcript_list])
    except (NoTranscriptFound, TranscriptsDisabled):
        return transcribe_audio_with_whisper(video_id)


def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🔁 No captions found — falling back to Whisper STT")

    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(yt_url)
    stream = yt.streams.filter(only_audio=True).first()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Download audio file
        input_path = os.path.join(tmpdir, "input_audio.mp4")
        output_path = os.path.join(tmpdir, "converted_audio.wav")
        stream.download(filename=input_path)

        # Step 2: Convert to .wav using ffmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1",  # Whisper prefers mono 16kHz
            output_path
        ], check=True)

        # Step 3: Transcribe with Whisper
        result = whisper_model.transcribe(output_path)
        return result["text"]
