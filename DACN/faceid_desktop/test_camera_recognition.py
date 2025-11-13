"""
Test nhận diện face từ camera với embeddings trong DB
Giúp debug vấn đề không nhận diện được
"""
import cv2
import numpy as np
import mysql.connector
from tensorflow.keras.models import load_model
import tensorflow as tf

def l2_normalize_func(x):
    return tf.nn.l2_normalize(x, axis=-1)

# Load model
print("🔄 Loading model...")
model = load_model('../AI/faceid_model_tf.h5', custom_objects={'l2_normalize_func': l2_normalize_func})
embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer('embedding_normalized').output)
print("✅ Model loaded")

# Load embeddings từ DB
print("🔄 Loading employee embeddings from DB...")
db = mysql.connector.connect(host='localhost', user='root', password='12345', database='attendance_db')
cursor = db.cursor()
cursor.execute("SELECT id, name, face_encoding FROM employees WHERE face_encoding IS NOT NULL ORDER BY photo_path")
employees = []
for emp_id, name, encoding in cursor.fetchall():
    embedding = np.frombuffer(encoding, dtype=np.float32)
    employees.append({'id': emp_id, 'name': name, 'embedding': embedding})
cursor.close()
db.close()
print(f"✅ Loaded {len(employees)} employees")

# Mở camera
print("\n📷 Opening camera... Press SPACE to capture, ESC to quit")
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

THRESHOLD = 0.45

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read from camera")
        break
    
    # Detect face
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    # Draw rectangle
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{len(faces)} face(s) detected", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow('Camera Test - Press SPACE to recognize', frame)
    
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
    elif key == 32 and len(faces) > 0:  # SPACE
        print("\n" + "="*60)
        print("🔍 RECOGNIZING...")
        (x, y, w, h) = faces[0]
        face_img = frame[y:y+h, x:x+w]
        
        # Convert BGR to RGB
        face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, (160, 160))
        face_array = np.array(face_resized) / 255.0
        face_array = np.expand_dims(face_array, axis=0)
        
        # Extract embedding
        query_embedding = embedding_model.predict(face_array, verbose=0)[0]
        print(f"Query embedding norm: {np.linalg.norm(query_embedding):.4f}")
        print(f"First 10 values: {query_embedding[:10]}")
        
        # Compare with all employees
        print("\n📊 Similarity scores:")
        best_match = None
        best_similarity = -1
        
        for emp in employees:
            similarity = np.dot(query_embedding, emp['embedding'])
            status = "✅ MATCH" if similarity >= THRESHOLD else "❌"
            print(f"   {emp['name']:<30} : {similarity:.4f} ({similarity*100:.1f}%) {status}")
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = emp
        
        print(f"\n{'='*60}")
        if best_match and best_similarity >= THRESHOLD:
            print(f"✅ RECOGNIZED: {best_match['name']} ({best_similarity*100:.1f}%)")
        else:
            print(f"❌ NO MATCH (best: {best_similarity*100:.1f}%, threshold: {THRESHOLD*100:.0f}%)")
        print(f"{'='*60}\n")

cap.release()
cv2.destroyAllWindows()
print("👋 Bye!")
