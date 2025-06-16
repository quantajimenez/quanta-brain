# quanta/utils/youtube_scraper.py

from pytube import Playlist, Channel

def get_playlist_videos(playlist_id: str) -> list:
    """Fetch all video IDs from a YouTube playlist."""
    try:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        playlist = Playlist(url)
        return [video.video_id for video in playlist.videos]
    except Exception as e:
        print(f"❌ Failed to fetch playlist videos: {e}")
        return []

def get_channel_uploads(channel_id: str) -> list:
    """Fetch recent video IDs from a YouTube channel's uploads."""
    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        channel = Channel(url)
        return [video.video_id for video in channel.videos]
    except Exception as e:
        print(f"❌ Failed to fetch channel uploads: {e}")
        return []
