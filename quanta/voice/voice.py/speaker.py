def send_alert(data):
    print("[QUANTA ALERT TRIGGERED]")
    print(f"Ticker: {data.get('ticker')}")
    print(f"Price: {data.get('price')}")
    print(f"Signal: {data.get('signal')}")
    print(f"Confidence: {data.get('confidence')}")
    print(f"Type: {data.get('Type')}, Strike: {data.get('strike')}")
    print(f"Expiry: {data.get('expiry')}")
    print(f"Session: {data.get('session')}")
