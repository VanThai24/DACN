"""
Script để import tất cả ảnh từ face_data vào database qua Flask API
"""
import requests
import os
from pathlib import Path

API_URL = "http://127.0.0.1:5000/add_face"
FACE_DATA_DIR = Path(__file__).parent / "face_data"

def add_face_to_db(image_path, name):
    """Gửi ảnh đến Flask API để thêm vào database"""
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {'name': name}
            response = requests.post(API_URL, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Added {name} from {image_path.name}")
                    return True
                else:
                    print(f"❌ Failed {name}: {result.get('reason')}")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code} for {name}")
                return False
    except Exception as e:
        print(f"❌ Error adding {name}: {e}")
        return False

def main():
    """Import tất cả ảnh từ face_data folders"""
    print("🚀 Starting face import...")
    print(f"📁 Face data directory: {FACE_DATA_DIR}")
    
    total = 0
    success = 0
    
    # Duyệt qua tất cả thư mục con trong face_data
    for person_folder in FACE_DATA_DIR.iterdir():
        if not person_folder.is_dir():
            continue
            
        person_name = person_folder.name
        print(f"\n📸 Processing: {person_name}")
        
        # Lấy tất cả ảnh trong folder
        image_files = list(person_folder.glob("*.jpg")) + \
                     list(person_folder.glob("*.jpeg")) + \
                     list(person_folder.glob("*.png"))
        
        if not image_files:
            print(f"  ⚠️  No images found in {person_name}")
            continue
        
        # Chỉ thêm 1 ảnh đầu tiên cho mỗi người (tránh duplicate)
        # Nếu muốn thêm tất cả, bỏ [:1]
        for img_path in image_files[:1]:  
            total += 1
            if add_face_to_db(img_path, person_name):
                success += 1
    
    print(f"\n✨ Import complete: {success}/{total} faces added")
    
    # Kiểm tra danh sách faces
    try:
        response = requests.get("http://127.0.0.1:5000/faces")
        if response.status_code == 200:
            faces = response.json().get('faces', [])
            print(f"\n📋 Total faces in database: {len(faces)}")
            for face in faces:
                print(f"   - {face['name']} (ID: {face['id']})")
    except Exception as e:
        print(f"❌ Error fetching faces: {e}")

if __name__ == "__main__":
    main()
