# quanta/ingest/youtube_pattern_agent.py

import os
import uuid
from datetime import datetime
from quanta.utils.logger import setup_logger
from quanta.crews.langchain_boot import boot_langchain_memory
from quanta.ingest.youtube_scraper import fetch_video_metadata, crawl_playlist, crawl_channel_uploads
from quanta.ingest.youtube_transcript_utils import extract_transcript
from quanta.utils.s3_uploader import upload_signal_to_s3
from langchain_core.documents import Document

logger = setup_logger("YouTubePatternAgent")

PATTERN_KEYWORDS = [
    "double top", "double bottom", "head and shoulders", "inverse head and shoulders",
    "cup and handle", "breakout", "support", "resistance",
    "RSI", "MACD", "moving average", "bullish", "bearish",
    "trend line", "channel", "ascending triangle", "descending triangle"
]

class YouTubePatternAgent:
    def __init__(self):
        logger.info("🧠 Booting LangChain memory...")
        self.llm, self.embeddings, self.vectorstore = boot_langchain_memory()

    def ingest_video(self, video_url: str):
        logger.info(f"🎥 Ingesting video: {video_url}")
        try:
            meta = fetch_video_metadata(video_url)
            transcript = extract_transcript(meta["video_id"])
            logger.info(f"📜 Transcript loaded ({len(transcript)} chars)")

            if not transcript.strip():
                logger.warning("⚠️ Empty transcript, skipping video.")
                return

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
            logger.info(f"🧠 Stored in FAISS: {pattern} from {meta['video_id']}")

            signal = {
                "id": str(uuid.uuid4()),
                "source": "youtube",
                "pattern": pattern,
                "title": meta["title"],
                "channel": meta["channel"],
                "video_id": meta["video_id"],
                "source_url": f"https://www.youtube.com/watch?v={meta['video_id']}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            upload_signal_to_s3(signal, prefix="youtube")

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


# 🔁 Entry point
if __name__ == "__main__":
    agent = YouTubePatternAgent()
    agent.ingest_channel("UCGL9ubdGcvZh_dvSV2z1hoQ")  # The Trading Channel
