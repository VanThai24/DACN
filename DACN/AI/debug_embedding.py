"""
Debug embedding comparison
"""
import numpy as np
import mysql.connector
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Sequential

# 1. Load TensorFlow model
model_path = r'D:\DACN\DACN\AI\faceid_model_tf.h5'
full_model = tf.keras.models.load_model(model_path)
_ = full_model.predict(np.zeros((1, 128, 128, 3)), verbose=0)

embedding_layers = full_model.layers[:-1]
partial_model = Sequential(embedding_layers)

# 2. Test với nhiều trường hợp
test_cases = [
    (r'D:\DACN\DACN\AI\face_data\Huy\2.png', 'Huy', 'Same person, different image'),
    (r'D:\DACN\DACN\AI\face_data\Quang\1.png', 'Huy', 'Different person (Quang vs Huy)'),
]

for img_path, db_name, desc in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {desc}")
    print(f"Query: {img_path}")
    print(f"DB: {db_name}")
    
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    query_embedding = partial_model.predict(img_array, verbose=0)[0]
    
    # Load embedding từ database
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='attendance_db',
        user='root',
        password='12345'
    )
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, face_embedding FROM employees WHERE name = %s', (db_name,))
    row = cursor.fetchone()
    
    if row:
        emp_id, name, embedding_blob = row
        db_embedding = np.frombuffer(embedding_blob, dtype=np.float64)
        
        # Calculate distance
        query_float64 = query_embedding.astype(np.float64)
        dist = np.linalg.norm(db_embedding - query_float64)
        
        print(f"📊 Distance: {dist:.4f}")
        print(f"   Should match: {desc.startswith('Same')}")
        print(f"   Result: {'MATCH ✅' if dist < 10 else 'NO MATCH ❌'} (threshold=10)")
    
    cursor.close()
    conn.close()

cursor.close()
conn.close()
