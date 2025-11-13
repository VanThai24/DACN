"""
Cập Nhật Embeddings Cho Tất Cả Nhân Viên
Sử dụng Best Model (face_recognition large)
"""

import os
import mysql.connector
import joblib
import face_recognition
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'faceid_best_model.pkl')
DATA_DIR = os.path.join(BASE_DIR, 'face_data')

print("=" * 80)
print("CẬP NHẬT EMBEDDINGS CHO NHÂN VIÊN TRONG DATABASE")
print("=" * 80)

# Load model
if not os.path.exists(MODEL_PATH):
    print(f"❌ Model không tồn tại: {MODEL_PATH}")
    print("Chạy: python train_best_model.py")
    exit(1)

clf = joblib.load(MODEL_PATH)
print(f"✅ Model loaded: {len(clf.classes_)} classes - {list(clf.classes_)}")

# Connect to database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

print("\n[1/2] Getting employees from database...")
cursor.execute("SELECT id, name FROM employees")
employees = cursor.fetchall()
print(f"✅ Found {len(employees)} employees in database")

# Update embeddings
print("\n[2/2] Updating embeddings...")

updated_count = 0
skipped_count = 0

for emp_id, emp_name in employees:
    print(f"\n  Processing: {emp_name} (ID: {emp_id})")
    
    # Tìm folder của nhân viên
    person_dir = os.path.join(DATA_DIR, emp_name)
    
    if not os.path.exists(person_dir):
        print(f"    ⚠️  Folder không tồn tại: {person_dir}")
        skipped_count += 1
        continue
    
    # Lấy tất cả ảnh và thử từng ảnh cho đến khi thành công
    image_files = [f for f in os.listdir(person_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_files) == 0:
        print(f"    ⚠️  Không có ảnh trong folder")
        skipped_count += 1
        continue
    
    # Thử tất cả ảnh cho đến khi extract được embedding
    embedding = None
    for img_file in image_files:
        img_path = os.path.join(person_dir, img_file)
        
        try:
            # Load với Unicode support
            with open(img_path, 'rb') as f:
                img_array = np.frombuffer(f.read(), dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if image is None:
                continue
            
            # Resize if too small
            h, w = image.shape[:2]
            if w < 300:
                scale = 300 / w
                image = cv2.resize(image, (int(w * scale), int(h * scale)))
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract embedding với model='large'
            face_encodings = face_recognition.face_encodings(image, model='large')
            
            if len(face_encodings) > 0:
                embedding = face_encodings[0]
                print(f"    ✅ Extracted from: {img_file}")
                break  # Found valid embedding
                
        except Exception as e:
            continue  # Try next image
    
    if embedding is None:
        print(f"    ❌ No valid face detected in any image")
        skipped_count += 1
        continue
    
    # Convert to blob (bytes)
    embedding_blob = embedding.astype(np.float32).tobytes()
    
    # Update database
    try:
        cursor.execute("""
            UPDATE employees 
            SET face_encoding = %s
            WHERE id = %s
        """, (embedding_blob, emp_id))
        
        db.commit()
        
        print(f"    ✅ Updated embedding (128-dim vector)")
        updated_count += 1
        
    except Exception as e:
        print(f"    ❌ Database error: {e}")
        skipped_count += 1

cursor.close()
db.close()

# Summary
print("\n" + "=" * 80)
print("🎉 CẬP NHẬT HOÀN TẤT!")
print("=" * 80)
print(f"✅ Updated: {updated_count} employees")
print(f"⚠️  Skipped: {skipped_count} employees")
print(f"✅ Total: {len(employees)} employees")

print("\n📋 Next steps:")
print("  1. Chạy desktop app: python faceid_desktop/main.py")
print("  2. Test face recognition với camera")
print("=" * 80)
