# quanta/ingest/youtube_scraper.py

import re
import os
from typing import List
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from googleapiclient.errors import HttpError

# Load key from environment (must be set manually or by Render)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Disable local API caching (avoids file permission issues on Windows)
class NoCache(Cache):
    def get(self, url): return None
    def set(self, url, content): pass

def get_youtube_service():
    if not YOUTUBE_API_KEY:
        raise Exception("❌ YOUTUBE_API_KEY not set in environment.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache=NoCache())

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def fetch_video_metadata(video_url: str) -> dict:
    """
    Retrieves title, channel, and other metadata from a single video URL.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("❌ Invalid YouTube URL format.")

    youtube = get_youtube_service()
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        if not response["items"]:
            raise Exception(f"❌ No video found for ID: {video_id}")

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
    """
    Crawls all video URLs from a YouTube playlist.
    """
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    playlist_id = match.group(1) if match else None
    if not playlist_id:
        raise Exception("❌ Invalid playlist URL.")

    youtube = get_youtube_service()
    video_urls = []

    try:
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
    except HttpError as e:
        raise Exception(f"❌ Playlist crawl failed: {e}")

def crawl_channel_uploads(channel_id: str, max_videos: int = 50) -> List[str]:
    """
    Crawls the 'uploads' playlist of a YouTube channel to get recent video URLs.
    """
    youtube = get_youtube_service()

    try:
        # Get the Uploads playlist ID from the channel's content details
        channel = youtube.channels().list(part="contentDetails", id=channel_id).execute()
        uploads_playlist_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        video_urls = []
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50,
            playlistId=uploads_playlist_id
        )

        while request and len(video_urls) < max_videos:
            response = request.execute()
            for item in response["items"]:
                video_id = item["contentDetails"]["videoId"]
                video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
            request = youtube.playlistItems().list_next(request, response)

        return video_urls
    except HttpError as e:
        raise Exception(f"❌ Channel crawl failed: {e}")

