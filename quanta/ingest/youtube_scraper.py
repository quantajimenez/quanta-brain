# quanta/ingest/youtube_scraper.py

import re
import os
from typing import List
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from googleapiclient.errors import HttpError

# Load API key from .env
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Prevent Windows write errors in discovery cache
class NoCache(Cache):
    def get(self, url): return None
    def set(self, url, content): pass

def get_youtube_service():
    if not YOUTUBE_API_KEY:
        raise Exception("❌ YOUTUBE_API_KEY not set. Add it to .env.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache=NoCache())

def extract_video_id(url: str) -> str:
    """
    Extracts video ID from YouTube URL.
    """
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_video_metadata(video_url: str) -> dict:
    """
    Fetches metadata for a single YouTube video by URL.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("❌ Invalid YouTube URL.")

    youtube = get_youtube_service()
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not response["items"]:
            raise E

