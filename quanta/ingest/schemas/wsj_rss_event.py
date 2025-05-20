from pydantic import BaseModel

class WSJRssEvent(BaseModel):
    headline: str
    ticker: str
    confidence: float = 0.0
