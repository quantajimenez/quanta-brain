# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import tempfile
import subprocess
import os
from pytube import YouTube
from faster_whisper import WhisperModel

whisper_model = WhisperModel("medium", compute_type="int8")


def extract_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([line['text'] for line in transcript_list])
    except (NoTranscriptFound, TranscriptsDisabled):
        return transcribe_audio_with_whisper(video_id)


def transcribe_audio_with_whisper(video_id: str) -> str:
    print("🔁 No captions found – falling back to Faster-Whisper STT")

    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(yt_url)

    # Download a progressive stream with audio + video
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not stream:
        raise Exception("No suitable stream found.")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.mp4")
        output_path = os.path.join(tmpdir, "converted.wav")

        print("📥 Downloading audio...")
        stream.download(filename=input_path)

        print("🎛️ Converting to mono WAV...")
        result = subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", output_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print("❌ FFmpeg failed:", result.stderr.decode())
            raise Exception("FFmpeg conversion failed.")

        print(f"📁 Output WAV size: {os.path.getsize(output_path)} bytes")

        print("🧠 Transcribing...")
        segments = whisper_model.transcribe(output_path)

        print("📄 Whisper result raw:", segments)

        if 'segments' not in segments or not segments['segments']:
            print("❌ No transcription segments.")
            return ""

        texts = [seg.text for seg in segments['segments']]
        return "\n".join(texts)
