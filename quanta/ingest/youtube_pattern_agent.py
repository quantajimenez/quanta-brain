# quanta/ingest/youtube_pattern_agent.py

import os
from quanta.ingest.youtube_scraper import fetch_video_metadata
from quanta.ingest.youtube_transcript_utils import extract_transcript
from quanta.utils.logger import setup_logger
from quanta.crews.langchain_boot import boot_langchain_memory
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger("YouTubePatternAgent")

# Define what patterns we want to detect
PATTERN_KEYWORDS = [
    "double top", "head and shoulders", "cup and handle",
    "breakout", "support", "resistance",
    "RSI", "MACD", "moving average", "bullish", "bearish"
]

class YouTubePatternAgent:
    def __init__(self):
        logger.info("🧠 Booting LangChain memory...")
        self.llm, self.embeddings, self.vectorstore = boot_langchain_memory()

    def ingest_video(self, video_url: str):
        logger.info(f"🎥 Processing video: {video_url}")
        
        meta = fetch_video_metadata(video_url)
        transcript = extract_transcript(meta['video_id'])
        logger.info(f"📝 Transcript extracted ({len(transcript)} chars)")

        patterns = self.extract_patterns(transcript)

        if not patterns:
            logger.warning("⚠️ No patterns found in transcript.")
            return

        self.store_memory(meta, transcript, patterns)
        logger.info(f"✅ Stored {len(patterns)} patterns: {patterns}")

    def extract_patterns(self, transcript: str):
        found = []
        lower_text = transcript.lower()
        for pattern in PATTERN_KEYWORDS:
            if pattern in lower_text:
                found.append(pattern)
        return list(set(found))

    def store_memory(self, meta: dict, transcript: str, patterns: list):
        for pattern in patterns:
            content = f"{meta['title']} | Pattern: {pattern} | Channel: {meta['channel']}\n\n{transcript[:500]}"
            doc = Document(page_content=content, metadata={
                "video_id": meta["video_id"],
                "pattern": pattern,
                "source_url": f"https://www.youtube.com/watch?v={meta['video_id']}"
            })
            self.vectorstore.add_documents([doc])
            logger.info(f"🧠 Memory saved for pattern: {pattern}")

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=PmhuPbY8ZHo"
    agent = YouTubePatternAgent()
    agent.ingest_video(test_url)

