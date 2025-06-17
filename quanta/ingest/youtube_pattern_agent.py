# quanta/ingest/youtube_pattern_agent.py

import os
import uuid
import json
import traceback

from quanta.utils.logger import setup_logger
from quanta.utils.s3_uploader import upload_signal_to_s3
from quanta.ingest.youtube_transcript_utils import extract_transcript
from quanta.ingest.youtube_scraper import get_playlist_videos, get_channel_uploads

logger = setup_logger("youtubePatternAgent")

# Sample pattern keywords
PATTERN_KEYWORDS = [
    "breakout", "double bottom", "head and shoulders", "inverse head and shoulders",
    "cup and handle", "support", "resistance",
    "bullish", "bearish", "momentum", "volume", "reversal"
]


class YouTubePatternAgent:
    def __init__(self):
        self.logger = logger
        self.processed = 0
        self.failed = 0

    def ingest_clip(self, video_id: str):
        try:
            transcript = extract_transcript(video_id)
            if not transcript or transcript.strip() == "":
                logger.warning(f"⚠️ Transcript blank, skipping video: {video_id}")
                self.failed += 1
                return

            patterns = self.extract_patterns(transcript)
            if not patterns:
                logger.info(f"ℹ️ No patterns found in video: {video_id}")
                return

            self.save_pattern_signal(video_id, transcript, patterns)
            self.processed += 1

        except Exception as e:
            logger.error(f"❌ Failed to ingest video {video_id}: {e}")
            traceback.print_exc()
            self.failed += 1

    def extract_patterns(self, transcript: str):
        found = []
        for word in PATTERN_KEYWORDS:
            if word.lower() in transcript.lower():
                found.append(word)
        return list(set(found))

    def save_pattern_signal(self, video_id: str, transcript: str, patterns: list):
        yt_url = f"https://www.youtube.com/watch?v={video_id}"

        data = {
            "id": str(uuid.uuid4()),
            "source": "youtube",
            "pattern": patterns[0],  # Optional: store only first match
            "title": "N/A",
            "channel": "N/A",
            "video_id": video_id,
            "source_url": yt_url,
            "timestamp": str(json.loads(json.dumps({"now": str(uuid.uuid1().time)}))["now"])
        }

        upload_signal_to_s3(data, prefix="youtube")
        logger.info(f"✅ Uploaded signal: {data}")

    def ingest_playlist(self, playlist_id: str, max_videos: int = 20):
        logger.info(f"📥 Ingesting playlist: {playlist_id}")
        try:
            video_ids = get_playlist_videos(playlist_id)[:max_videos]
            for vid in video_ids:
                self.ingest_clip(vid)
        except Exception as e:
            logger.error(f"❌ Failed playlist ingest: {e}")

    def ingest_channel(self, channel_id: str, max_videos: int = 20):
        logger.info(f"📥 Ingesting channel uploads: {channel_id}")
        try:
            video_ids = get_channel_uploads(channel_id)[:max_videos]
            for vid in video_ids:
                self.ingest_clip(vid)
        except Exception as e:
            logger.error(f"❌ Failed channel ingest: {e}")


if __name__ == "__main__":
    agent = YouTubePatternAgent()
    # Replace with your actual playlist or channel
    agent.ingest_clip("vbM2R2CM96Q&t=5s")
    logger.info(f"✅ Done. Signals processed: {agent.processed}, failed: {agent.failed}")


