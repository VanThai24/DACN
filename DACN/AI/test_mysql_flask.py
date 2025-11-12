"""
Test Flask server đọc embeddings từ MySQL
"""
import requests

url = "http://127.0.0.1:5000/faces"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            faces = data['faces']
            print(f"✅ Flask server đọc được {len(faces)} khuôn mặt từ MySQL:")
            for face in faces:
                print(f"   - ID {face['id']}: {face['name']}")
        else:
            print("❌ API returned success=False")
    else:
        print(f"❌ HTTP error {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
