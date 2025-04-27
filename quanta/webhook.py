# webhook.py
from flask import Flask, request
import requests
import os

app = Flask(__name__)

def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        print("✅ Telegram response:", response.text)
    except Exception as e:
        print("❌ Telegram send error:", e)

@app.route("/")
def home():
    return "📡 Quanta Webhook is Live"

@app.route("/tradingview", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Incoming JSON:", data)

        if "message" in data:
            data = data["message"]

        ticker = data.get("ticker")
        price = data.get("price")
        signal = data.get("signal")
        confidence = data.get("confidence")
        option_type = data.get("option_type")
        strike = data.get("strike")
        expiry = data.get("expiry")
        session = data.get("session")
        source = data.get("source", "TradingView")

        if ticker and price and signal:
            message = (
                f"📊 {source} Alert:\n"
                f"Ticker: {ticker}\n"
                f"Price: {price}\n"
                f"Signal: {signal}\n"
                f"Confidence: {confidence or 'N/A'}\n"
            )
            if option_type:
                message += f"Type: {option_type}\n"
            if strike:
                message += f"Strike: {strike}\n"
            if expiry:
                message += f"Expiry: {expiry}\n"
            if session:
                message += f"Session: {session}\n"
        else:
            message = f"⚠️ Alert received, but missing fields:\n{data}"

        send_telegram_message(message)
        return "✅ Alert forwarded"
    except Exception as e:
        print("❌ Webhook error:", e)
        return "❌ Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # 🚨 PORT 10000 not 8080!
