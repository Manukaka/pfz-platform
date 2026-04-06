import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_fisherman_flow():
    print("--- Starting Fisherman Flow Test ---")

    # 1. Fisherman requests access
    req_data = {
        "name": "Test Fisherman",
        "boat_name": "Sea Queen",
        "phone": "9876543210"
    }
    resp = requests.post(f"{BASE_URL}/api/auth/request-access", json=req_data)
    print(f"Request Access: {resp.status_code} - {resp.json()}")
    request_id = resp.json()["request_id"]

    # 2. Admin logs in to approve
    admin_login = {
        "username": "manukaka",
        "password": "Ashu@9970"
    }
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=admin_login)
    print(f"Admin Login: {resp.status_code}")
    admin_token = resp.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Admin lists requests
    resp = requests.get(f"{BASE_URL}/api/auth/admin/requests", headers=admin_headers)
    requests_list = resp.json()
    print(f"Admin Requests List: Found {len(requests_list)} requests")

    # 4. Admin approves request
    approve_data = {"request_id": request_id, "hours": 12}
    resp = requests.post(f"{BASE_URL}/api/auth/admin/approve", json=approve_data, headers=admin_headers)
    print(f"Approve Request: {resp.status_code} - {resp.json()}")
    access_key = resp.json()["access_key"]

    # 5. Fisherman logs in using Access Key
    fisherman_login = {
        "username": "testfisherman", # generated from name in request
        "password": access_key
    }
    resp = requests.post(f"{BASE_URL}/api/auth/login", json=fisherman_login)
    print(f"Fisherman Login: {resp.status_code} - {resp.json()}")
    fisherman_token = resp.json()["token"]
    fisherman_headers = {"Authorization": f"Bearer {fisherman_token}"}

    # 6. Check session status
    resp = requests.get(f"{BASE_URL}/api/auth/session-status", headers=fisherman_headers)
    print(f"Session Status: {resp.status_code} - {resp.json()}")

    # 7. Admin lists active sessions
    resp = requests.get(f"{BASE_URL}/api/auth/admin/sessions", headers=admin_headers)
    print(f"Admin Active Sessions: {resp.json()}")

    print("--- Test Completed ---")

if __name__ == "__main__":
    test_fisherman_flow()
