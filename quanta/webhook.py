from flask import Flask, request, jsonify

app = Flask(__name__)  # ✅ Define the Flask app instance

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    try:
        data = request.get_json()
        print("📩 Webhook received:", data)  # Optional: Log to console

        # Forward to voice or analysis module
        from quanta.voice import telegram_alerts
        telegram_alerts.send_insight_alert(data)

        return jsonify({"status": "success", "message": "Webhook processed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
