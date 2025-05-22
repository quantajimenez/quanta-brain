# quanta/ingest/youtube_scraper.py

import re
from typing import List
from googleapiclient.discovery import build
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Must be set in Render
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def fetch_video_metadata(video_url: str) -> dict:
    video_id = extract_video_id(video_url)
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    if not response["items"]:
        raise Exception(f"No video found for ID: {video_id}")
    data = response["items"][0]["snippet"]
    return {
        "video_id": video_id,
        "title": data["title"],
        "channel": data["channelTitle"],
        "published_at": data["publishedAt"],
        "description": data.get("description", "")
    }

def crawl_playlist(playlist_url: str) -> List[str]:
    match = re.search(r"list=([a-zA-Z0-9_-]+)", playlist_url)
    playlist_id = match.group(1) if match else None
    if not playlist_id:
        raise Exception("Invalid playlist URL.")
    
    video_urls = []
    request = youtube.playlistItems().list(part="contentDetails", maxResults=50, playlistId=playlist_id)
    while request:
        response = request.execute()
        for item in response["items"]:
            video_id = item["contentDetails"]["videoId"]
            video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
        request = youtube.playlistItems().list_next(request, response)
    return video_urls

