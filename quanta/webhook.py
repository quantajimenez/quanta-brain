# webhook.py
from flask import Flask
import boto3
import os

app = Flask(__name__)

# Wasabi Settings (from Render environment variables)
WASABI_ACCESS_KEY = os.getenv('WASABI_ACCESS_KEY')
WASABI_SECRET_KEY = os.getenv('WASABI_SECRET_KEY')
WASABI_ENDPOINT = 'https://s3.us-east-1.wasabisys.com'
BUCKET_NAME = 'quanta-stock-data'

@app.route('/')
def home():
    return "✅ Quanta Realtime Webhook Running"

@app.route('/test_wasabi')
def test_wasabi_connection():
    try:
        session = boto3.session.Session()
        s3 = session.client('s3',
            endpoint_url=WASABI_ENDPOINT,
            aws_access_key_id=WASABI_ACCESS_KEY,
            aws_secret_access_key=WASABI_SECRET_KEY
        )

        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
            return f"✅ Wasabi Connection Successful. {len(files)} files found:<br>" + "<br>".join(files)
        else:
            return "⚠️ Wasabi Connection OK, but no files found in bucket."
    except Exception as e:
        return f"❌ Wasabi Connection Failed: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
