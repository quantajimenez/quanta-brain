# quanta/brain/youtube_router.py

from fastapi import APIRouter
from quanta.utils.s3_reader import list_youtube_signals

router = APIRouter()

@router.get("/youtube_signals")
def get_youtube_signals(limit: int = 10):
    return list_youtube_signals(limit=limit)

