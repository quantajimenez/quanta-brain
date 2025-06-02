# quanta/ingest/youtube_job_producer.py

import redis

r = redis.from_url("redis://localhost:6379")  # or use env var if needed

def produce_jobs(video_urls):
    for url in video_urls:
        r.lpush("quanta_jobs_youtube", url)
        print(f"✅ Enqueued: {url}")

if __name__ == "__main__":
    urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://www.youtube.com/watch?v=xyz456"
    ]
    produce_jobs(urls)

