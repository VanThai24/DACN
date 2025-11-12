"""
Debug scan matching - kiểm tra distance và embedding compatibility
"""
import requests
import numpy as np

BASE_URL = "http://127.0.0.1:5000"

# Test với cùng 1 người
print("Testing scan with Huy image 2.png (should match ID 71)...")
test_image = r"D:\DACN\DACN\AI\face_data\Huy\2.png"

with open(test_image, 'rb') as f:
    files = {'image': ('test.jpg', f, 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/scan", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if 'distance' in result:
        print(f"\n📊 Distance: {result['distance']:.4f}")
        print(f"   Threshold: 10.0 (TensorFlow model)")
        print(f"   Match: {'YES ✅' if result.get('success') else 'NO ❌'}")
        if result.get('success'):
            print(f"   👤 Recognized: {result.get('name')} (ID {result.get('id')})")
