# quanta/ingest/payload_parser.py

from quanta.ingest.schemas.tradingview_event import TradingViewEvent
from quanta.ingest.schemas.polygon_event import PolygonEvent
from quanta.ingest.schemas.yahoo_event import YahooEvent
from quanta.ingest.schemas.wsj_rss_event import WSJRssEvent

def parse_payload(data):
    # Try each schema in turn, return the first that matches
    try:
        if 'ticker' in data and 'price' in data:
            # TradingView or Polygon
            try:
                return {"valid": True, "payload": TradingViewEvent(**data)}
            except Exception:
                return {"valid": True, "payload": PolygonEvent(**data)}
        elif 'headline' in data:
            try:
                return {"valid": True, "payload": YahooEvent(**data)}
            except Exception:
                return {"valid": True, "payload": WSJRssEvent(**data)}
        else:
            return {"valid": False, "error": "Unrecognized payload schema"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

