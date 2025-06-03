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
            url_str = url.decode("utf-8")  # ✅ decode once here
            print(f"🚀 Processing: {url_str}")
            agent.ingest_video(url_str)
        else:
            print("🕐 No jobs. Sleeping...")
            time.sleep(10)

if __name__ == "__main__":
    worker_loop()
