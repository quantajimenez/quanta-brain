# quanta/execution/trade_outcome_log.py

def log_trade_outcome(ticker, result, pnl, confidence, reason=""):
    print(f"[TRADE OUTCOME] Ticker: {ticker} | Result: {result} | PnL: {pnl} | Confidence: {confidence} | Reason: {reason}")
