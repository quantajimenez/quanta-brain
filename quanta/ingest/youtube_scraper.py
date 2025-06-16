# quanta/ingest/youtube_scraper.py

from pytube import Playlist, Channel

def get_playlist_videos(playlist_id: str, max_videos: int = 20) -> list:
    """Fetch video IDs from a public YouTube playlist using pytube."""
    try:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        playlist = Playlist(url)
        return [video.video_id for video in playlist.videos[:max_videos]]
    except Exception as e:
        print(f"❌ Failed to fetch playlist videos: {e}")
        return []

def get_channel_uploads(channel_id: str, max_videos: int = 20) -> list:
    """Fetch recent video IDs from a public YouTube channel using pytube."""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        channel = Channel(url)
        return [video.video_id for video in channel.videos[:max_videos]]
    except Exception as e:
        print(f"❌ Failed to fetch channel uploads: {e}")
        return []

