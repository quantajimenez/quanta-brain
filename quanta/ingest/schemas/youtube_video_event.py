# quanta/ingest/schemas/youtube_video_event.py

from pydantic import BaseModel
from typing import List, Optional

class YouTubeVideoEvent(BaseModel):
    video_id: str
    title: str
    channel: str
    transcript: Optional[str]
    patterns: List[str]
    embedded_chunks: int
    source_url: str

    class Config:
        schema_extra = {
            "example": {
                "video_id": "PmhuPbY8ZHo",
                "title": "How to Trade Like a Pro",
                "channel": "The Trading Channel",
                "transcript": "This is where we talk about the double top...",
                "patterns": ["double top", "RSI"],
                "embedded_chunks": 3,
                "source_url": "https://www.youtube.com/watch?v=PmhuPbY8ZHo"
            }
        }

