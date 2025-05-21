import os
import time
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

REQUIRED_ENV_VARS = [
    "POLYGON_S3_ACCESS_KEY",
    "POLYGON_S3_SECRET_KEY",
    "OPENAI_API_KEY",
    "RENDER_API_KEY",
    "RENDER_SERVICE_ID",
    "GITHUB_TOKEN",
    "HUGGINGFACE_API_TOKEN"
]

logger = logging.getLogger("MonitoringAgent")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            logger.info("Health check received.")
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server(port=8181):
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthHandler)
    logger.info(f"Diagnostics/monitoring HTTP server running on port {port}...")
    httpd.serve_forever()

def check_env_vars():
    logger.info("Checking required environment variables...")
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        logger.error(f"Missing environment variables: {missing}")
        return False
    logger.info("All required environment variables are set.")
    return True

def health_check():
    logger.info("Performing health check...")
    try:
        import requests
        resp = requests.get("https://www.google.com", timeout=5)
        if resp.status_code == 200:
            logger.info("Internet access: OK")
        else:
            logger.error("Internet access failed.")
            return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
    return True

def periodic_self_check(interval=300):
    while True:
        env_ok = check_env_vars()
        system_ok = health_check()
        if env_ok and system_ok:
            logger.info("Self-diagnostics: Agent is healthy.")
        else:
            logger.error("Critical system issue detected. Initiate auto-recovery (TBD).")
        time.sleep(interval)

def main():
    # Start HTTP /health server in a separate thread
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()
    try:
        periodic_self_check()
    except KeyboardInterrupt:
        logger.info("Monitoring agent shutting down.")

if __name__ == "__main__":
    main()
