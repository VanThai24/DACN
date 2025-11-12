"""
Test Flask AI server đọc embeddings từ database
"""
import requests

API_URL = "http://127.0.0.1:5000"

print("🔍 Testing Flask AI Server...")
print(f"📍 Server: {API_URL}\n")

# Test 1: Kiểm tra danh sách faces
print("1️⃣ Test /faces endpoint:")
try:
    response = requests.get(f"{API_URL}/faces", timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            faces = data.get('faces', [])
            print(f"   ✅ Tìm thấy {len(faces)} khuôn mặt trong database")
            for face in faces:
                print(f"      - {face['name']} (ID: {face['id']})")
        else:
            print(f"   ❌ API returned success=False")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Kiểm tra embedding từ get_all_embeddings
print("\n2️⃣ Test get_all_embeddings function:")
print("   (Cần import trực tiếp từ app.py)")
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from app import get_all_embeddings
    
    embeddings = get_all_embeddings()
    print(f"   ✅ Đọc được {len(embeddings)} embeddings")
    for name, emb in embeddings:
        print(f"      - {name}: shape {emb.shape}, dtype {emb.dtype}")
    
    if len(embeddings) > 0 and embeddings[0][1].shape[0] == 128:
        print("\n🎉 SERVER ĐANG SỬ DỤNG EMBEDDING 128 CHIỀU!")
    else:
        print(f"\n❌ Server vẫn dùng embedding {embeddings[0][1].shape[0] if embeddings else '?'} chiều!")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Test hoàn tất!")
