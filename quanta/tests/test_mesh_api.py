# quanta/tests/test_mesh_api.py

import requests

def check_api():
    base_url = "http://localhost:12000"
    endpoints = [
        ("/agents", "GET"),
        ("/mesh/health", "GET"),
        ("/audit/logs?n=5", "GET"),
    ]
    print("\n[API ENDPOINT TEST]")
    for route, method in endpoints:
        url = f"{base_url}{route}"
        try:
            if method == "GET":
                resp = requests.get(url)
            else:
                resp = requests.post(url)
            print(f"{method} {route} -> status {resp.status_code}")
            print(resp.json())
        except Exception as e:
            print(f"ERROR on {method} {route}: {e}")

if __name__ == "__main__":
    check_api()
