import cv2
import numpy as np
import mysql.connector
from tensorflow.keras.models import load_model
import tensorflow as tf

# Custom function cho model
def l2_normalize_func(x):
    return tf.nn.l2_normalize(x, axis=-1)

# Load model
model = load_model('../AI/faceid_model_tf.h5', custom_objects={'l2_normalize_func': l2_normalize_func})
embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer('embedding_normalized').output)

# Lấy embedding từ DB
db = mysql.connector.connect(host='localhost', user='root', password='12345', database='attendance_db')
cursor = db.cursor()
cursor.execute("SELECT name, photo_path, face_encoding FROM employees WHERE face_encoding IS NOT NULL LIMIT 1")
row = cursor.fetchone()
name, photo_path, db_encoding = row
db_embedding = np.frombuffer(db_encoding, dtype=np.float32)

print(f"Employee: {name}")
print(f"Photo path: {photo_path}")
print(f"DB embedding norm: {np.linalg.norm(db_embedding):.4f}")
print(f"DB embedding first 10: {db_embedding[:10]}")

# Extract embedding từ ảnh mới - PHẢI CROP FACE
face_data_path = f'../AI/face_data/{photo_path}'
import os
images = []
for img_name in os.listdir(face_data_path)[:3]:  # Lấy 3 ảnh
    img_path = os.path.join(face_data_path, img_name)
    img_bgr = cv2.imread(img_path)
    if img_bgr is not None:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # 🔥 CROP FACE (giống migrate_to_embedding.py và main.py)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_img = img_rgb[y:y+h, x:x+w]
        else:
            face_img = img_rgb
        
        face_resized = cv2.resize(face_img, (160, 160))
        face_array = face_resized.astype('float32') / 255.0
        images.append(face_array)

if images:
    images = np.array(images)
    new_embeddings = embedding_model.predict(images, verbose=0)
    
    print(f"\n--- Extracted {len(new_embeddings)} new embeddings ---")
    for i, emb in enumerate(new_embeddings):
        similarity = np.dot(db_embedding, emb)
        print(f"Image {i+1}:")
        print(f"  Norm: {np.linalg.norm(emb):.4f}")
        print(f"  First 10: {emb[:10]}")
        print(f"  Similarity with DB: {similarity:.4f}")

cursor.close()
db.close()
