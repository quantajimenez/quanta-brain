# quanta/utils/github_writer.py

import os
import base64
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

API_BASE = "https://api.github.com"

def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def read_file_from_github(path):
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"
    response = requests.get(url, headers=_headers())
    if response.status_code == 200:
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8")
    else:
        print(f"[GITHUB READ ERROR] {response.status_code}: {response.text}")
        return None

def write_file_to_github(path, content, commit_message):
    url = f"{API_BASE}/repos/{GITHUB_REPO}/contents/{path}"

    # Check if file exists to fetch SHA
    get_response = requests.get(url, headers=_headers())
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": "main"
    }

    if sha:
        payload["sha"] = sha  # Include for updates

    response = requests.put(url, headers=_headers(), json=payload)
    if response.status_code in [200, 201]:
        print(f"[GITHUB WRITE SUCCESS] {path}")
        return True
    else:
        print(f"[GITHUB WRITE ERROR] {response.status_code}: {response.text}")
        return False
