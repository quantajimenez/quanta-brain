from pydantic import BaseModel

class YahooEvent(BaseModel):
    headline: str
    ticker: str
    impact: float = 0.0
