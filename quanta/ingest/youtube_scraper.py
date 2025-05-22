# quanta/ingest/youtube_scraper.py

import re
import os
from typing import List
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from googleapiclient.errors import HttpError

# Load from environment variable (Render or .env)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Disable Google API local file caching (fixes Windows issues)
class NoCache(Cache):
    def get(self, url): return None
    def set(self, url, content): pass

def get_youtube_service():
    if not YOUTUBE_API_KEY:
        raise Exception("❌ YOUTUBE_API_KEY not set.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache=NoCache())

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def fetch_video_metadata(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("❌ Invalid YouTube URL format.")
    
    youtube = get_youtube_service()
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not response["items"]:
            raise Exception(f"❌ No metadata found for video ID: {video_id}")
        
        data = response["items"][0]["snippet"]
        return {
            "video_id": video_id,
            "title": data["title"],
            "channel": data["channelTitle"],
            "published_at": data["publishedAt"],
            "description": data.get("description", "")
        }
    except HttpError as e:
        raise Exception(f"❌ YouTube API error: {e}")

def crawl_playlist(playlist_url: str) -> List[str]:
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    playlist_id = match.group(1) if match else None
    if not playlist_id:
        raise Exception("❌ Invalid playlist URL.")
    
    youtube = get_youtube_service()
    video_urls = []
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=50,
        playlistId=playlist_id
    )

    while request:
        response = request.execute()
        for item in response["items"]:
            video_id = item["contentDetails"]["videoId"]
            video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
        request = youtube.playlistItems().list_next(request, response)

    return video_urls

