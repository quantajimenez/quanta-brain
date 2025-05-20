# quanta/ingest/webhook_listener.py

from fastapi import FastAPI, Request
from quanta.ingest.payload_parser import parse_payload
from quanta.ingest.ingestor_agent import ingest_event
from quanta.ingest.alerts import send_insight_alert

app = FastAPI()

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    try:
        data = await request.json()
        parsed = parse_payload(data)
        if not parsed['valid']:
            send_insight_alert(f"Invalid payload: {parsed['error']}")
            return {"status": "error", "detail": parsed['error']}
        ingest_event(parsed['payload'])
        return {"status": "success"}
    except Exception as e:
        send_insight_alert(f"Webhook exception: {str(e)}")
        return {"status": "error", "detail": str(e)}

