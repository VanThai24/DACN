"""
Test Best Model với Webcam
Real-time face recognition với model đã train
"""

import cv2
import face_recognition
import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'faceid_best_model.pkl')
METADATA_PATH = os.path.join(BASE_DIR, 'faceid_best_model_metadata.pkl')

print("=" * 80)
print("TEST BEST MODEL VỚI WEBCAM")
print("=" * 80)

# Load model
if not os.path.exists(MODEL_PATH):
    print(f"❌ Model không tồn tại: {MODEL_PATH}")
    print("Chạy: python train_best_model.py")
    exit(1)

print(f"Loading model: {MODEL_PATH}")
clf = joblib.load(MODEL_PATH)

# Load metadata
metadata = joblib.load(METADATA_PATH)

print(f"✅ Model loaded")
print(f"✅ Classes: {len(clf.classes_)} - {list(clf.classes_)}")
print(f"✅ Train Accuracy: {metadata['train_accuracy']*100:.2f}%")
print(f"✅ Test Accuracy: {metadata['test_accuracy']*100:.2f}%")
print(f"✅ Avg Confidence: {metadata['avg_confidence']*100:.2f}%")
print(f"✅ Best params: {metadata['best_params']}")

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Không thể mở webcam!")
    exit(1)

print("\n✅ Webcam opened")
print("\n🎥 Bắt đầu nhận diện...")
print("📋 Hướng dẫn:")
print("  - Green box: Confidence ≥ 60%")
print("  - Yellow box: 40% ≤ Confidence < 60%")
print("  - Red box: Confidence < 40%")
print("  - Press 'q' to quit")
print("=" * 80)

frame_count = 0
process_every_n_frames = 3  # Process every 3 frames

# Load face detector for faster detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Display frame even when not processing
    if frame_count % process_every_n_frames != 0:
        cv2.imshow('Face Recognition - Best Model', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Fast face detection with Haar Cascade first
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_haar = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces_haar) == 0:
        cv2.putText(frame, "No face detected", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('Face Recognition - Best Model', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
    
    # Find faces with face_recognition (more accurate)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model='large')
    
    # Draw boxes and labels
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Predict
        face_encoding = face_encoding.reshape(1, -1)
        
        prediction = clf.predict(face_encoding)[0]
        proba = clf.predict_proba(face_encoding)[0]
        confidence = np.max(proba) * 100
        
        # Get top 3 predictions
        top_3_idx = np.argsort(proba)[::-1][:3]
        top_3_names = [clf.classes_[i] for i in top_3_idx]
        top_3_probs = [proba[i] * 100 for i in top_3_idx]
        
        # Color based on confidence
        if confidence >= 60:
            color = (0, 255, 0)  # Green - HIGH confidence
        elif confidence >= 40:
            color = (0, 255, 255)  # Yellow - MEDIUM confidence
        else:
            color = (0, 0, 255)  # Red - LOW confidence
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
        
        # Draw main label
        label = f"{prediction} ({confidence:.1f}%)"
        
        # Background for text
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, label, (left + 6, bottom - 6), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        # Draw top 3 predictions beside face
        y_offset = top
        for i, (name, prob) in enumerate(zip(top_3_names, top_3_probs)):
            text = f"{i+1}. {name}: {prob:.1f}%"
            cv2.putText(frame, text, (right + 10, y_offset + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # Display info
    info_text = f"Detected: {len(face_locations)} face(s) | Frame: {frame_count}"
    cv2.putText(frame, info_text, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Display frame
    cv2.imshow('Face Recognition - Best Model', frame)
    
    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

print("\n✅ Test completed")
print("\n📊 Summary:")
print(f"  Model: {MODEL_PATH}")
print(f"  Classes: {list(clf.classes_)}")
print(f"  Test Accuracy: {metadata['test_accuracy']*100:.2f}%")
print("\nNếu kết quả tốt, có thể tích hợp vào desktop app!")
