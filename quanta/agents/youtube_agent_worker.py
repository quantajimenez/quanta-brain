# quanta/agents/youtube_agent_worker.py

import redis
import time
from quanta.ingest.youtube_pattern_agent import YouTubePatternAgent

r = redis.from_url("redis://localhost:6379")

def worker_loop():
    agent = YouTubePatternAgent()
    while True:
        url = r.rpop("quanta_jobs_youtube")
        if url:
            print(f"🚀 Processing: {url}")
            agent.ingest_video(url.decode("utf-8"))
        else:
            print("🕒 No jobs. Sleeping...")
            time.sleep(10)

if __name__ == "__main__":
    worker_loop()

