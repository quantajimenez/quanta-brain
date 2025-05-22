# quanta/ingest/youtube_pattern_agent.py

import os
from quanta.utils.logger import setup_logger
from quanta.crews.langchain_boot import boot_langchain_memory
from quanta.ingest.youtube_scraper import (
    fetch_video_metadata,
    crawl_playlist,
    crawl_channel_uploads
)
from quanta.ingest.youtube_transcript_utils import extract_transcript
from langchain_core.documents import Document

logger = setup_logger("YouTubePatternAgent")

# Define technical patterns to detect in transcripts
PATTERN_KEYWORDS = [
    "double top", "double bottom", "head and shoulders", "inverse head and shoulders",
    "cup and handle", "breakout", "support", "resistance",
    "RSI", "MACD", "moving average", "bullish", "bearish",
    "trend line", "channel", "ascending", "descending"
]

class YouTubePatternAgent:
    def __init__(self):
        logger.info("🧠 Initializing LangChain memory...")
        self.llm, self.embeddings, self.vectorstore = boot_langchain_memory()

    def ingest_video(self, video_url: str):
        try:
            logger.info(f"🎥 Ingesting video: {video_url}")
            meta = fetch_video_metadata(video_url)
            transcript = extract_transcript(meta["video_id"])
            logger.info(f"📝 Transcript loaded ({len(transcript)} chars)")

            patterns = self.extract_patterns(transcript)

            if not patterns:
                logger.warning("⚠️ No patterns found in transcript.")
                return

            self.store_memory(meta, transcript, patterns)
            logger.info(f"✅ Stored patterns: {patterns}")

        except Exception as e:
            logger.error(f"❌ Failed to ingest video: {e}")

    def extract_patterns(self, transcript: str):
        found = []
        lower_text = transcript.lower()
        for pattern in PATTERN_KEYWORDS:
            if pattern in lower_text:
                found.append(pattern)
        return list(set(found))

    def store_memory(self, meta: dict, transcript: str, patterns: list):
        for pattern in patterns:
            content = f"{meta['title']} | {meta['channel']} | Pattern: {pattern}\n\n{transcript[:500]}"
            doc = Document(
                page_content=content,
                metadata={
                    "video_id": meta["video_id"],
                    "pattern": pattern,
                    "channel": meta["channel"],
                    "source_url": f"https://www.youtube.com/watch?v={meta['video_id']}"
                }
            )
            self.vectorstore.add_documents([doc])
            logger.info(f"🧠 Stored in memory: {pattern} from {meta['video_id']}")

    def ingest_playlist(self, playlist_url: str, max_videos: int = 20):
        logger.info(f"📺 Ingesting playlist: {playlist_url}")
        try:
            video_urls = crawl_playlist(playlist_url)
            for url in video_urls[:max_videos]:
                self.ingest_video(url)
        except Exception as e:
            logger.error(f"❌ Failed playlist ingest: {e}")

    def ingest_channel(self, channel_id: str, max_videos: int = 20):
        logger.info(f"📡 Ingesting channel uploads: {channel_id}")
        try:
            video_urls = crawl_channel_uploads(channel_id, max_videos)
            for url in video_urls:
                self.ingest_video(url)
        except Exception as e:
            logger.error(f"❌ Failed channel ingest: {e}")

if __name__ == "__main__":
    agent = YouTubePatternAgent()

    # ✅ Test with single video
    agent.ingest_video("https://www.youtube.com/watch?v=PmhuPbY8ZHo")

    # ✅ Test with playlist
    # agent.ingest_playlist("https://www.youtube.com/playlist?list=PLKE_22Jx497twaT62Qv9DAiagynP4dAYV")

    # ✅ Test with channel ID
    # agent.ingest_channel("UC3tM4HZozu-hT8f0sC0noyg")  # The Trading Channel


