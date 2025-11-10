import requests

# Test API nhận diện khuôn mặt (scan)
def test_scan_faceid():
    # Lấy JWT token
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {"username": "testuser", "password": "123456"}
    resp = requests.post(login_url, json=login_data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json().get("access_token")
    assert token, "No access_token returned"

    # Gửi embedding giả lên API scan
    scan_url = "http://localhost:8000/api/faceid/scan"
    headers = {"Authorization": f"Bearer {token}"}
    embedding = [0.1] * 128  # embedding giả
    resp2 = requests.post(scan_url, json={"encodings": embedding}, headers=headers)
    print("Scan response:", resp2.status_code, resp2.text)
    assert resp2.status_code == 200 or resp2.status_code == 400, f"Scan failed: {resp2.text}"

if __name__ == "__main__":
    test_scan_faceid()
