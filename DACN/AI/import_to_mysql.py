"""
Import face embeddings vào MySQL database (attendance_db)
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing import image
from db import get_db_connection

# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# Load model
MODEL_PATH = 'faceid_model_tf.h5'
model = tf.keras.models.load_model(MODEL_PATH, custom_objects={'l2_normalize_func': l2_normalize_func})
print(f"✅ Model loaded from {MODEL_PATH}")
print(f"📊 Model layers: {len(model.layers)}")

def get_embedding_from_model(img_path):
    """Trích xuất embedding 128-dim từ ảnh"""
    # Model được train với input size 160x160 (không phải 128x128)
    img = image.load_img(img_path, target_size=(160, 160))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict qua tất cả layers
    _ = model.predict(img_array, verbose=0)
    
    # Lấy output trực tiếp từ layer -2
    # Tạo partial model bằng cách slice layers
    from tensorflow.keras.models import Sequential
    embedding_layers = model.layers[:-1]  # Bỏ layer cuối (classification)
    partial_model = Sequential(embedding_layers)
    
    embedding = partial_model.predict(img_array, verbose=0)[0]
    return embedding

def import_faces_to_mysql():
    """Import faces từ face_data/ vào MySQL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    face_data_dir = 'face_data'
    imported_count = 0
    
    # Lấy danh sách employees hiện có
    cursor.execute('SELECT id, name FROM employees')
    existing_employees = {row[1]: row[0] for row in cursor.fetchall()}
    print(f"📋 Found {len(existing_employees)} employees in MySQL database")
    
    # Duyệt qua từng folder trong face_data
    for person_name in os.listdir(face_data_dir):
        person_folder = os.path.join(face_data_dir, person_name)
        if not os.path.isdir(person_folder):
            continue
            
        print(f"\n👤 Processing: {person_name}")
        
        # Lấy ảnh đầu tiên trong folder
        images = [f for f in os.listdir(person_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            print(f"   ⚠️  No images found in {person_folder}")
            continue
            
        img_path = os.path.join(person_folder, images[0])
        
        try:
            # Trích xuất embedding
            embedding = get_embedding_from_model(img_path)
            embedding_bytes = embedding.astype(np.float64).tobytes()
            
            print(f"   ✅ Embedding shape: {embedding.shape}")
            
            # Kiểm tra xem employee đã tồn tại chưa
            if person_name in existing_employees:
                employee_id = existing_employees[person_name]
                # Update embedding cho employee có sẵn
                cursor.execute(
                    'UPDATE employees SET face_embedding = %s WHERE id = %s',
                    (embedding_bytes, employee_id)
                )
                print(f"   ✅ Updated embedding for employee ID {employee_id}")
            else:
                # Tạo employee mới (không có position column)
                cursor.execute(
                    'INSERT INTO employees (name, face_embedding, department) VALUES (%s, %s, %s)',
                    (person_name, embedding_bytes, 'AI')
                )
                employee_id = cursor.lastrowid
                print(f"   ✅ Created new employee ID {employee_id}")
                
            imported_count += 1
            conn.commit()
            
        except Exception as e:
            print(f"   ❌ Error processing {person_name}: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\n✨ Import complete: {imported_count} faces processed")

if __name__ == '__main__':
    import_faces_to_mysql()
