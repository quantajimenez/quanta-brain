# quanta/ingest/youtube_scraper.py

from pytube import Playlist, Channel

def get_playlist_videos(playlist_id: str, max_videos: int = 20) -> list:
    """
    Fetch video IDs from a YouTube playlist using pytube.

    Args:
        playlist_id (str): The YouTube playlist ID.
        max_videos (int): Max number of videos to return.

    Returns:
        list: List of video IDs.
    """
    try:
        url = f"https://www.youtube.com/playlist?list={playlist_id}"
        print(f"🔗 Fetching playlist: {url}")
        playlist = Playlist(url)
        videos = [video.video_id for video in playlist.videos[:max_videos]]
        print(f"📺 Found {len(videos)} videos in playlist.")
        return videos
    except Exception as e:
        import traceback
        print(f"❌ Failed to fetch playlist videos: {e}")
        traceback.print_exc()
        return []


def get_channel_uploads(channel_id: str, max_videos: int = 20) -> list:
    from pytube import Channel

    try:
        url = f"https://www.youtube.com/channel/{channel_id}"
        print(f"🔗 Fetching channel: {url}")
        channel = Channel(url)

        # Materialize generator into a list
        video_list = list(channel.videos)

        videos = [video.video_id for video in video_list[:max_videos]]
        print(f"📹 Found {len(videos)} videos in channel.")
        return videos

    except Exception as e:
        import traceback
        print(f"❌ Failed to fetch channel uploads: {e}")
        traceback.print_exc()
        return []

