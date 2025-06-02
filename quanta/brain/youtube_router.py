# quanta/brain/youtube_router.py

from fastapi import APIRouter, Query
from quanta.utils.s3_reader import list_youtube_signals
from quanta.ingest.youtube_pattern_agent import YouTubePatternAgent

router = APIRouter()

@router.get("/youtube_signals")
def get_youtube_signals():
    """
    Lists all YouTube insight objects stored in the S3 bucket.
    """
    try:
        files = list_youtube_signals()
        return {"youtube_insights": files}
    except Exception as e:
        return {"error": str(e)}

@router.post("/ingest")
def ingest_youtube_url(url: str = Query(..., description="YouTube video URL to process")):
    """
    Triggers YouTube ingestion for a single video URL.
    """
    try:
        agent = YouTubePatternAgent()
        agent.ingest_video(url)
        return {"status": "Ingestion complete", "url": url}
    except Exception as e:
        return {"error": str(e)}

@router.get("/latest")
def latest_youtube_signals():
    """
    Stub for future: Return parsed content of latest_youtube_signals.json.
    """
    try:
        return list_youtube_signals()  # Or custom logic to read latest
    except Exception as e:
        return {"error": str(e)}

