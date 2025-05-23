from fastapi import APIRouter
from quanta.utils.s3_reader import list_youtube_signals

router = APIRouter()

@router.get("/youtube_signals")
def get_youtube_signals():
    """
    Returns a list of YouTube-related insight files from S3.
    """
    try:
        files = list_youtube_signals()
        return {"youtube_insights": files}
    except Exception as e:
        return {"error": str(e)}

