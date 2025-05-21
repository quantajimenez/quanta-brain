# quanta/ingest/schemas/polygon_event.py

from pydantic import BaseModel, Field
from typing import Optional

class PolygonEvent(BaseModel):
    # Common fields
    ticker: str                                 # Underlying symbol (e.g., 'SPY', 'TSLA', 'NVDA')
    event_type: str = Field(..., description="Type of event: 'stock_bar' or 'option_bar'")
    timestamp: int                              # Unix epoch millis
    datetime: str                               # ISO-8601 UTC time

    # Bar data (for both stocks and options)
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None
    num_trades: Optional[int] = None            # Number of trades in this interval
    exchange: Optional[str] = None              # Market center or exchange code
    conditions: Optional[str] = None            # Trade conditions

    # Option-specific fields (None for stock events)
    option_symbol: Optional[str] = None         # Option contract symbol (e.g., 'TSLA240621C00300000')
    strike_price: Optional[float] = None
    expiration_date: Optional[str] = None       # ISO date, e.g., '2024-06-21'
    option_type: Optional[str] = None           # 'call' or 'put'
    open_interest: Optional[int] = None
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "ticker": "TSLA",
                "event_type": "option_bar",
                "timestamp": 1716223800000,
                "datetime": "2024-05-21T15:00:00Z",
                "open": 12.0,
                "high": 13.5,
                "low": 11.5,
                "close": 12.8,
                "volume": 152,
                "vwap": 12.7,
                "num_trades": 7,
                "exchange": "OPRA",
                "conditions": "regular",
                "option_symbol": "TSLA240621C00300000",
                "strike_price": 300.0,
                "expiration_date": "2024-06-21",
                "option_type": "call",
                "open_interest": 1220,
                "implied_volatility": 0.62,
                "delta": 0.55,
                "gamma": 0.12,
                "theta": -0.03,
                "vega": 0.09,
            }
        }
