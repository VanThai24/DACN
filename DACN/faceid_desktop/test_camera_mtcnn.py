"""
IMPROVED: Test với MTCNN face detection (tốt hơn Haar Cascade)
"""
import cv2
import numpy as np
import mysql.connector
from tensorflow.keras.models import load_model
import tensorflow as tf
from mtcnn import MTCNN

def l2_normalize_func(x):
    return tf.nn.l2_normalize(x, axis=-1)

# Load model
print("🔄 Loading models...")
model = load_model('../AI/faceid_model_tf.h5', custom_objects={'l2_normalize_func': l2_normalize_func})
embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer('embedding_normalized').output)
detector = MTCNN()
print("✅ Models loaded")

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

THRESHOLD = 0.40  # Giảm xuống 40% vì MTCNN detect tốt hơn

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read from camera")
        break
    
    # Detect face với MTCNN
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_frame)
    
    # Draw rectangle
    for face in faces:
        x, y, w, h = face['box']
        confidence = face['confidence']
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{len(faces)} face(s) - conf:{confidence:.2f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow('Camera Test - Press SPACE to recognize', frame)
    
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
    elif key == 32 and len(faces) > 0:  # SPACE
        print("\n" + "="*60)
        print("🔍 RECOGNIZING WITH MTCNN...")
        face = faces[0]
        x, y, w, h = face['box']
        face_img = rgb_frame[y:y+h, x:x+w]
        
        face_resized = cv2.resize(face_img, (160, 160))
        face_array = np.array(face_resized) / 255.0
        face_array = np.expand_dims(face_array, axis=0)
        
        # Extract embedding
        query_embedding = embedding_model.predict(face_array, verbose=0)[0]
        print(f"Query embedding norm: {np.linalg.norm(query_embedding):.4f}")
        print(f"MTCNN confidence: {face['confidence']:.3f}")
        
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
