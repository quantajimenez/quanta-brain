import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Agent health info - simple shared dict for demo purposes
agent_health = {
    "polygon_s3_ingest": {"status": "unknown", "last_heartbeat": 0},
    "monitoring_agent": {"status": "unknown", "last_heartbeat": 0},
    # Add more agents as needed
}

def agent_heartbeat(agent, status="ok"):
    agent_health[agent]["status"] = status
    agent_health[agent]["last_heartbeat"] = int(time.time())

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(agent_health).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_status_server(port=8181):
    httpd = HTTPServer(('', port), StatusHandler)
    print(f"Agent health server running at http://0.0.0.0:{port}/health")
    httpd.serve_forever()

if __name__ == "__main__":
    # In real usage, agents would periodically update their health
    def fake_heartbeat():
        while True:
            agent_heartbeat("polygon_s3_ingest", status="ok")
            agent_heartbeat("monitoring_agent", status="ok")
            time.sleep(60)
    threading.Thread(target=fake_heartbeat, daemon=True).start()
    run_status_server()
