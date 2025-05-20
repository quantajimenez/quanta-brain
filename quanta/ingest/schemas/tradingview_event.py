from pydantic import BaseModel

class TradingViewEvent(BaseModel):
    ticker: str
    price: float
    # Add fields as needed

