# quanta/ingest/youtube_transcript_utils.py

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import os
import whisper
import tempfile
from pytube import YouTube
from pydub import AudioSegment

whisper_model = whisper.load_model("base")

def extract_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([line['text'] for line in transcript_list])
    except (NoTranscriptFound, TranscriptsDisabled):
        return transcribe_audio(video_id)

def transcribe_audio(video_id: str) -> str:
    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(yt_url)
    stream = yt.streams.filter(only_audio=True).first()
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_audio:
        stream.download(filename=temp_audio.name)
        audio = AudioSegment.from_file(temp_audio.name)
        audio.export(temp_audio.name.replace(".mp4", ".wav"), format="wav")
        result = whisper_model.transcribe(temp_audio.name.replace(".mp4", ".wav"))
        return result["text"]

