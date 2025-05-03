from flask import request, jsonify

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    try:
        data = request.get_json()
        print("📩 Webhook received:", data)  # Optional: Log to console

        # Example: forward to voice or analysis module
        from quanta.voice import telegram_alerts
        telegram_alerts.send_insight_alert(data)

        return jsonify({"status": "success", "message": "Webhook processed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
