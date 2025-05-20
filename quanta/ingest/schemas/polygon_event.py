from pydantic import BaseModel

class PolygonEvent(BaseModel):
    ticker: str
    price: float
    volume: int = 0
    # Add fields as needed
