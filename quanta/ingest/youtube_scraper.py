# quanta/ingest/youtube_scraper.py

import os
from googleapiclient.discovery import build

# Set this in your .env or environment
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def _get_youtube_service():
    if not YOUTUBE_API_KEY:
        raise ValueError("❌ Missing YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_channel_uploads(channel_id: str, max_videos: int = 20) -> list:
    try:
        youtube = _get_youtube_service()

        # Step 1: get uploads playlist ID
        channel_resp = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        uploads_playlist_id = channel_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Step 2: fetch videos from the uploads playlist
        return get_playlist_videos(uploads_playlist_id, max_videos)
    except Exception as e:
        print(f"❌ YouTube Data API error (channel uploads): {e}")
        return []

def get_playlist_videos(playlist_id: str, max_videos: int = 20) -> list:
    try:
        youtube = _get_youtube_service()
        video_ids = []
        next_page_token = None

        while len(video_ids) < max_videos:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(50, max_videos - len(video_ids)),
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_ids.append(video_id)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        print(f"📺 Fetched {len(video_ids)} videos from playlist.")
        return video_ids

    except Exception as e:
        print(f"❌ YouTube Data API error (playlist): {e}")
        return []
