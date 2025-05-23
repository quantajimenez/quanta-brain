from fastapi import FastAPI, Request
import logging

app = FastAPI()

@app.post("/insight")
async def insight(request: Request):
    data = await request.json()
    logging.info(f"Received insight: {data}")
    # TODO: Relay to Telegram/Slack/etc.
    return {"status": "received", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quanta.connect.connect_api:app", host="0.0.0.0", port=10020, reload=True)
