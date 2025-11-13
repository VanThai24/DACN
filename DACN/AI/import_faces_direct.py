"""
Script thêm face embeddings trực tiếp vào database
Sử dụng TensorFlow model để tạo embeddings
"""
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import sqlite3
import os
from pathlib import Path

# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# Paths
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "faceid_model_tf.h5"
DB_PATH = BASE_DIR.parent / "backend_src" / "dacn.db"
FACE_DATA_DIR = BASE_DIR / "face_data"

print(f"🔧 Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(str(MODEL_PATH), custom_objects={'l2_normalize_func': l2_normalize_func})

# Build model để có input shape (160x160, không phải 128x128)
model.build((None, 160, 160, 3))

print("✅ Model loaded successfully")
print(f"📏 Model output dimension: {model.output_shape[-1]}")
print("⚠️  Sử dụng layer -2 (Dense 128) thay vì layer cuối (Dense 6)")

# Hàm helper để lấy embedding từ layer trước cuối
def get_embedding_from_model(img_array):
    """Lấy output từ layer Dense(128) thay vì Dense(6)"""
    # Tạo model mới chỉ đến layer -2
    embedding_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=model.layers[-2].output
    )
    return embedding_model.predict(img_array, verbose=0)[0]

def process_image(img_path):
    """Load and preprocess image for model"""
    try:
        # Model được train với input size 160x160
        img = image.load_img(img_path, target_size=(160, 160))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"❌ Error processing {img_path}: {e}")
        return None

def add_face_to_db(person_name, img_path):
    """Add face embedding to database"""
    # Process image
    img_array = process_image(img_path)
    if img_array is None:
        return False
    
    # Get embedding using helper function
    embedding = get_embedding_from_model(img_array)
    embedding_bytes = embedding.astype(np.float64).tobytes()
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        # Check if employee exists
        c.execute('SELECT id FROM employees WHERE name = ?', (person_name,))
        existing = c.fetchone()
        
        if existing:
            # Update existing employee
            c.execute('UPDATE employees SET face_embedding = ? WHERE name = ?', 
                     (embedding_bytes, person_name))
            print(f"✅ Updated face for: {person_name}")
        else:
            # Create new employee
            c.execute('''INSERT INTO employees 
                        (name, face_embedding, department, role, is_locked) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (person_name, embedding_bytes, 'IT', 'employee', 0))
            print(f"✅ Added new employee: {person_name}")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Database error for {person_name}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Import all faces from face_data directory"""
    print(f"\n🚀 Starting face import to: {DB_PATH}")
    print(f"📁 Reading from: {FACE_DATA_DIR}\n")
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    total = 0
    success = 0
    
    # Process each person folder
    for person_folder in FACE_DATA_DIR.iterdir():
        if not person_folder.is_dir():
            continue
        
        person_name = person_folder.name
        print(f"📸 Processing: {person_name}")
        
        # Get first image
        image_files = list(person_folder.glob("*.jpg")) + \
                     list(person_folder.glob("*.jpeg")) + \
                     list(person_folder.glob("*.png"))
        
        if not image_files:
            print(f"  ⚠️  No images found")
            continue
        
        # Use first image
        img_path = image_files[0]
        print(f"  📄 Using: {img_path.name}")
        
        total += 1
        if add_face_to_db(person_name, img_path):
            success += 1
    
    print(f"\n✨ Import complete: {success}/{total} faces added\n")
    
    # Verify
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('SELECT id, name FROM employees WHERE face_embedding IS NOT NULL')
    rows = c.fetchall()
    conn.close()
    
    print(f"📋 Total employees with faces: {len(rows)}")
    for row in rows:
        print(f"   - ID {row[0]}: {row[1]}")

if __name__ == "__main__":
    main()
