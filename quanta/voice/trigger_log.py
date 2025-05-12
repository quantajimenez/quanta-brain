# quanta/voice/trigger_log.py

def log_trigger_event(ticker, signal, confidence, status="SENT"):
    print(f"[TRIGGER LOG] Ticker: {ticker} | Signal: {signal} | Confidence: {confidence} | Status: {status}")
