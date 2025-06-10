# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import tempfile
import subprocess
import os
from pytube import YouTube
from faster_whisper import WhisperModel

# Load model once
whisper_model = WhisperModel("base", compute_type="int8")  # or float16 for GPU

def extract_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([line['text'] for line in transcript_list])
    except (NoTranscriptFound, TranscriptsDisabled):
        return transcribe_audio_with_whisper(video_id)

def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🔁 No captions found — falling back to Faster-Whisper STT")

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

        segments, _ = whisper_model.transcribe(output_path)
        return " ".join([segment.text for segment in segments])
