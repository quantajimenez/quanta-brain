# quanta/tests/test_mesh_api.py

import requests

def test_api():
    base_url = "http://localhost:12000"
    print("GET /agents:", requests.get(f"{base_url}/agents").json())
    print("GET /mesh/health:", requests.get(f"{base_url}/mesh/health").json())
    print("GET /audit/logs:", requests.get(f"{base_url}/audit/logs?n=10").json())

if __name__ == "__main__":
    test_api()
