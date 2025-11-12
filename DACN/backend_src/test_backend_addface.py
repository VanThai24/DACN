"""
Test backend /api/faceid/add_face endpoint
"""
import requests

url = "http://localhost:8000/api/faceid/add_face"

# Sử dụng ảnh test từ face_data
test_image = r"D:\DACN\DACN\AI\face_data\Huy\1.png"

with open(test_image, 'rb') as f:
    files = {'image': ('test.jpg', f, 'image/jpeg')}
    data = {'name': 'Test Huy'}
    
    print("📤 Sending request to backend...")
    response = requests.post(url, files=files, data=data)
    
    print(f"📊 Status: {response.status_code}")
    print(f"📝 Response: {response.json()}")
    
    if response.status_code == 201:
        result = response.json()
        if result.get('success'):
            embedding_size = result.get('embedding_size', 0)
            print(f"✅ Success! Embedding size: {embedding_size} dimensions")
        else:
            print(f"❌ Failed: {result.get('message')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
