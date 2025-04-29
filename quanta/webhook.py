# webhook.py

from flask import Flask
from quanta import background_worker  # ✅ NEW: Import background_worker
from quanta import wasabi_connector  # ✅ Already needed for /test_wasabi

app = Flask(__name__)

@app.route("/")
def home():
    return "Quanta is alive."

@app.route("/test_wasabi")
def test_wasabi():
    try:
        files = wasabi_connector.list_files_in_wasabi()
        return f"✅ Wasabi Connection Successful. {len(files)} files found:<br><br>" + "<br>".join(files)
    except Exception as e:
        return f"❌ Error connecting to Wasabi: {str(e)}"

@app.route("/test_download")
def test_download():
    try:
        background_worker.download_and_extract_files()  # ✅ NEW: Trigger download
        return "✅ Background worker triggered and completed!"
    except Exception as e:
        return f"❌ Error triggering background worker: {str(e)}"
