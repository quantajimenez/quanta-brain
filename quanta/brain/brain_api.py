import os
import boto3
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import json
import logging

app = FastAPI(title="Quanta Brain API", version="1.0")

# Robust logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# S3 config
S3_BUCKET = os.getenv("S3_INSIGHTS_BUCKET", "quanta-insights")
S3_KEY = os.getenv("S3_INSIGHTS_KEY", "latest_signals.json")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

def fetch_latest_signals():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=AWS_REGION,
    )
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(obj["Body"].read().decode())
    except Exception as e:
        logging.error(f"Error fetching latest signals from S3: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Error fetching latest signals: {str(e)}")

@app.get("/latest_signals")
def get_latest_signals():
    data = fetch_latest_signals()
    return JSONResponse(content=data)

@app.post("/insight")
async def receive_insight(request: Request):
    try:
        data = await request.json()
        logging.info(f"[INSIGHT] Received: {data}")
        # Optionally: Save to S3, DB, or trigger further processing here
        return JSONResponse(content={"status": "ok", "received": data}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"[INSIGHT] Error receiving insight: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@app.get("/")
def root():
    return {"status": "Quanta Brain API is live"}
