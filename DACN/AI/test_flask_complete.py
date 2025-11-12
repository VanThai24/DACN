"""
Test Flask AI server với MySQL database
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("TEST FLASK AI SERVER - MySQL Integration")
print("=" * 60)

# Test 1: Lấy danh sách faces
print("\n1️⃣ Testing GET /faces")
try:
    response = requests.get(f"{BASE_URL}/faces")
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            faces = data['faces']
            print(f"   ✅ Found {len(faces)} faces in MySQL:")
            for face in faces[:10]:  # Show first 10
                print(f"      - ID {face['id']}: {face['name']}")
            if len(faces) > 10:
                print(f"      ... and {len(faces) - 10} more")
        else:
            print("   ❌ API returned success=False")
    else:
        print(f"   ❌ HTTP error {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Verify embeddings in database
print("\n2️⃣ Verifying embeddings in MySQL")
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='attendance_db',
        user='root',
        password='12345'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, LENGTH(face_embedding) FROM employees WHERE face_embedding IS NOT NULL')
    rows = cursor.fetchall()
    
    print(f"   ✅ MySQL has {len(rows)} employees with embeddings:")
    for row in rows:
        print(f"      - ID {row[0]}: {row[1]} ({row[2]} bytes)")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ MySQL Error: {e}")

# Test 3: Test add_face với ảnh mới
print("\n3️⃣ Testing POST /add_face (using TensorFlow model)")
test_image = r"D:\DACN\DACN\AI\face_data\Quang\Quang.jpg"
try:
    with open(test_image, 'rb') as f:
        files = {'image': ('test.png', f, 'image/png')}
        data = {'name': 'Test Quang Flask'}
        
        response = requests.post(f"{BASE_URL}/add_face", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Face added successfully!")
                print(f"      - Name: {result.get('name')}")
                print(f"      - Embedding size: {result.get('embedding_size')} dimensions")
            else:
                print(f"   ❌ Failed: {result.get('reason')}")
        else:
            print(f"   ❌ HTTP error {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test scan với face_recognition library
print("\n4️⃣ Testing POST /scan (face recognition)")
scan_image = r"D:\DACN\DACN\AI\face_data\Huy\Huy.jpg"  # Use different person
try:
    with open(scan_image, 'rb') as f:
        files = {'image': ('test.png', f, 'image/png')}
        
        response = requests.post(f"{BASE_URL}/scan", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Face recognized!")
                print(f"      - Name: {result.get('name')}")
                print(f"      - ID: {result.get('id')}")
                print(f"      - Distance: {result.get('distance', 0):.4f}")
            else:
                print(f"   ⚠️  No match found: {result.get('reason')}")
        else:
            print(f"   ❌ HTTP error {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✨ Testing complete!")
print("=" * 60)
