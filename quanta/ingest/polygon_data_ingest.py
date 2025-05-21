# quanta/ingest/polygon_data_ingest.py

import os
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import List

from quanta.ingest.schemas.polygon_event import PolygonEvent
from quanta.ingest.logging_utils import log_event
from quanta.crews.langchain_boot import boot_langchain_memory

logger = logging.getLogger("PolygonIngestAgent")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

class PolygonIngestAgent:
    def __init__(self):
        if not POLYGON_API_KEY:
            raise Exception("POLYGON_API_KEY not set in environment variables")
        self.api_key = POLYGON_API_KEY
        self.llm, self.embeddings, self.vectorstore = boot_langchain_memory()

    def _build_stock_bar_url(self, ticker: str, timespan: str, from_date: str, to_date: str) -> str:
        return f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{timespan}/{from_date}/{to_date}?adjusted=true&sort=asc&limit=50000&apiKey={self.api_key}"

    def _build_option_bar_url(self, option_symbol: str, from_date: str, to_date: str) -> str:
        # 5-min bars, for the option contract
        return f"https://api.polygon.io/v2/aggs/ticker/{option_symbol}/range/5/minute/{from_date}/{to_date}?adjusted=true&sort=asc&limit=50000&apiKey={self.api_key}"

    def get_option_contracts(self, underlying: str, date: str) -> List[dict]:
        # Get all option contracts for this underlying and date
        url = f"https://api.polygon.io/v3/reference/options/contracts?underlying_ticker={underlying}&as_of={date}&limit=1000&apiKey={self.api_key}"
        contracts = []
        resp = requests.get(url)
        if resp.status_code == 200:
            results = resp.json()
            for contract in results.get('results', []):
                contracts.append(contract)
        else:
            logger.error(f"Failed to get option contracts: {resp.text}")
        return contracts

    def run_batch(self, tickers: List[str], start_date: str, end_date: str):
        """Batch ingest for all tickers (stocks and options) between start_date and end_date (YYYY-MM-DD)."""
        logger.info(f"Starting batch ingest for {tickers} from {start_date} to {end_date}")
        # Stocks: 1-min bars
        for ticker in tickers:
            self._batch_stock_bars(ticker, start_date, end_date)
            self._batch_options_bars(ticker, start_date, end_date)

    def _batch_stock_bars(self, ticker: str, start_date: str, end_date: str):
        url = self._build_stock_bar_url(ticker, "minute", start_date, end_date)
        resp = requests.get(url)
        if resp.status_code != 200:
            logger.error(f"Error fetching stock bars for {ticker}: {resp.text}")
            return
        bars = resp.json().get("results", [])
        logger.info(f"Pulled {len(bars)} stock bars for {ticker}")
        for bar in bars:
            event = PolygonEvent(
                ticker=ticker,
                event_type="stock_bar",
                timestamp=bar.get("t"),
                datetime=datetime.utcfromtimestamp(bar.get("t") / 1000).isoformat() + "Z",
                open=bar.get("o"),
                high=bar.get("h"),
                low=bar.get("l"),
                close=bar.get("c"),
                volume=bar.get("v"),
                vwap=bar.get("vw"),
                num_trades=bar.get("n"),
                exchange=None,
                conditions=None
            )
            self.validate_and_store(event.dict())

    def _batch_options_bars(self, underlying: str, start_date: str, end_date: str):
        # For each day, get contracts, then fetch 5-min bars for each
        day = datetime.strptime(start_date, "%Y-%m-%d")
        end_day = datetime.strptime(end_date, "%Y-%m-%d")
        while day <= end_day:
            as_of = day.strftime("%Y-%m-%d")
            contracts = self.get_option_contracts(underlying, as_of)
            logger.info(f"{as_of}: Found {len(contracts)} option contracts for {underlying}")
            for contract in contracts:
                try:
                    symbol = contract.get("ticker")
                    if not symbol:
                        continue
                    bars_url = self._build_option_bar_url(symbol, as_of, as_of)
                    resp = requests.get(bars_url)
                    if resp.status_code != 200:
                        logger.warning(f"Failed to get bars for {symbol}: {resp.text}")
                        continue
                    bars = resp.json().get("results", [])
                    for bar in bars:
                        event = PolygonEvent(
                            ticker=underlying,
                            event_type="option_bar",
                            timestamp=bar.get("t"),
                            datetime=datetime.utcfromtimestamp(bar.get("t") / 1000).isoformat() + "Z",
                            open=bar.get("o"),
                            high=bar.get("h"),
                            low=bar.get("l"),
                            close=bar.get("c"),
                            volume=bar.get("v"),
                            vwap=bar.get("vw"),
                            num_trades=bar.get("n"),
                            exchange=None,
                            conditions=None,
                            option_symbol=symbol,
                            strike_price=contract.get("strike_price"),
                            expiration_date=contract.get("expiration_date"),
                            option_type=contract.get("type"),
                            open_interest=bar.get("oi") if "oi" in bar else None,
                            implied_volatility=bar.get("iv") if "iv" in bar else None,
                            delta=None,
                            gamma=None,
                            theta=None,
                            vega=None,
                        )
                        self.validate_and_store(event.dict())
                except Exception as e:
                    logger.error(f"Option bar ingest error: {e}")
            day += timedelta(days=1)

    def validate_and_store(self, event_dict):
        try:
            event = PolygonEvent(**event_dict)
            doc = f"{event.event_type}|{event.ticker}|{event.datetime}|{event.close}"  # simple text for now
            metadata = event.dict()
            self.vectorstore.add_texts([doc], metadatas=[metadata])
            log_event({"event": event.event_type, "symbol": event.ticker, "timestamp": event.datetime, "ok": True})
        except Exception as e:
            log_event({"error": str(e), "event": event_dict})
            logger.error(f"Store failed: {e}")

    def run_live(self, tickers: List[str]):
        logger.info("Starting live ingest for tickers: %s", tickers)
        try:
            while True:
                now = datetime.utcnow()
                for ticker in tickers:
                    from_date = (now - timedelta(minutes=5)).strftime("%Y-%m-%d")
                    to_date = now.strftime("%Y-%m-%d")
                    self._batch_stock_bars(ticker, from_date, to_date)
                    self._batch_options_bars(ticker, from_date, to_date)
                time.sleep(300)  # Sleep for 5 minutes between live pulls
        except KeyboardInterrupt:
            logger.info("Live ingest stopped by user.")

# Example CLI usage
if __name__ == "__main__":
    tickers = ["SPY", "NVDA", "TSLA"]
    agent = PolygonIngestAgent()
    # Batch ingest recent 2 years for test, then expand
    agent.run_batch(tickers, "2022-01-01", "2024-05-21")
    # To start live ingest: agent.run_live(tickers)
