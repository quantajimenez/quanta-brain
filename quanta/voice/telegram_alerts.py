def send_insight_alert(data):
    from .speaker import send_alert
    send_alert(data)  # Right now, this just prints to shell/log
