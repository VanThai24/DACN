"""
Main.py mới - Dùng EMBEDDING MATCHING thay vì classification
KHÔNG CẦN TRAIN LẠI khi thêm nhân viên mới!
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
import cv2
import mysql.connector
import numpy as np

class FaceIDApp(QWidget):
    def get_jwt_token(self, username, password):
        import requests
        url = "http://localhost:8000/api/auth/login"
        data = {"username": username, "password": password}
        try:
            resp = requests.post(url, json=data)
            if resp.status_code == 200 and "access_token" in resp.json():
                return resp.json()["access_token"]
        except Exception as ex:
            print(f"[JWT ERROR] {ex}")
        return None
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceID Scan - Employee Lobby")
        self.setFixedSize(700, 520)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)
        self.title = QLabel("<h1 style='color:#1565c0; margin-bottom:16px;'>Quét FaceID Nhân Viên</h1>")
        self.title.setAlignment(Qt.AlignCenter)
        self.label = QLabel("Camera đã tắt.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 22px; color: #333; margin-bottom: 16px; font-weight: bold;")
        self.cam_view = QLabel()
        self.cam_view.setFixedSize(600, 340)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet("background: #f5f7fa; border-radius: 32px; margin: 24px auto 8px auto; border: 4px solid #1976d2; padding: 4px;")
        self.cam_btn = QPushButton("Bật Camera")
        self.cam_btn.setStyleSheet("font-size: 22px; background-color: #1565c0; color: white; padding: 8px 0; border-radius: 16px; margin-top: 32px; font-weight: bold;")
        self.cam_btn.clicked.connect(self.toggle_camera)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cam_view, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)
        self.layout.addWidget(self.cam_btn)
        self.cap = None
        self.camera_running = False
        self.setLayout(self.layout)
        self.setStyleSheet("background: #e3f2fd; border-radius: 24px;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def toggle_camera(self):
        # Lấy JWT token
        jwt_token = self.get_jwt_token("testuser", "123456")

        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.label.setText("Không mở được camera!")
                return
            self.camera_running = True
            self.cam_btn.setText("Tắt Camera")
            self.label.setText("Camera đang bật. Đưa khuôn mặt vào khung hình để xác thực...")
            scanned = False
            
            from PySide6.QtGui import QImage, QPixmap
            import tensorflow as tf
            import os
            
            # Custom function for L2 normalization
            def l2_normalize_func(x):
                return tf.nn.l2_normalize(x, axis=1)
            
            # Load model và tạo embedding model
            model_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_model_tf.h5')
            full_model = tf.keras.models.load_model(model_path, custom_objects={'l2_normalize_func': l2_normalize_func})
            
            # 🔥 QUAN TRỌNG: Tạo embedding model (bỏ classification layer)
            embedding_model = tf.keras.Model(
                inputs=full_model.input,
                outputs=full_model.get_layer('embedding_normalized').output
            )
            print(f"✅ Embedding model loaded: {embedding_model.output_shape}")
            
            # 🔥 Load embeddings từ database (thay vì dùng class_names)
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345",
                database="attendance_db"
            )
            cursor = db.cursor()
            # Lấy tất cả nhân viên có embedding (dùng face_embedding hoặc face_encoding)
            cursor.execute("""
                SELECT id, name, 
                       COALESCE(face_encoding, face_embedding) as encoding
                FROM employees 
                WHERE face_encoding IS NOT NULL OR face_embedding IS NOT NULL
            """)
            employees = cursor.fetchall()
            cursor.close()
            db.close()
            
            # Parse embeddings
            employee_data = []
            for emp_id, name, encoding_blob in employees:
                if encoding_blob:
                    # Blob là bytes, convert về numpy array
                    encoding = np.frombuffer(encoding_blob, dtype=np.float32)
                    employee_data.append({
                        'id': emp_id,
                        'name': name,
                        'embedding': encoding
                    })
            
            print(f"✅ Loaded {len(employee_data)} employees with embeddings")
            
            while self.camera_running:
                ret, frame = self.cap.read()
                if not ret:
                    self.label.setText("Không thể lấy hình ảnh từ camera!")
                    break
                    
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.cam_view.setPixmap(QPixmap.fromImage(qt_img).scaled(self.cam_view.size(), Qt.KeepAspectRatio))
                
                # Phát hiện khuôn mặt
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                
                if len(faces) > 0 and not scanned:
                    self.label.setText("Đã phát hiện khuôn mặt, đang xác thực bằng AI...")
                    (x, y, w, h) = faces[0]
                    face_img = rgb_frame[y:y+h, x:x+w]
                    
                    try:
                        # Resize và preprocess
                        face_resized = cv2.resize(face_img, (160, 160))
                        face_array = np.array(face_resized) / 255.0
                        face_array = np.expand_dims(face_array, axis=0)
                        
                        # 🔥 Trích xuất embedding (128-dim vector)
                        query_embedding = embedding_model.predict(face_array, verbose=0)[0]
                        
                        # 🔥 So sánh với tất cả embeddings trong database
                        best_match = None
                        best_similarity = -1
                        
                        for emp in employee_data:
                            # Cosine similarity (vì đã L2 normalized)
                            similarity = np.dot(query_embedding, emp['embedding'])
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_match = emp
                        
                        # 🔥 Threshold để nhận diện
                        THRESHOLD = 0.6  # Càng cao càng chặt (0.5-0.7 là hợp lý)
                        
                        if best_match and best_similarity >= THRESHOLD:
                            emp_name = best_match['name']
                            confidence_pct = best_similarity * 100
                            self.label.setText(f"✅ Điểm danh: {emp_name} ({confidence_pct:.1f}%)")
                            
                            # Gửi lên backend
                            import requests
                            headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
                            scan_url = "http://localhost:8000/api/faceid/scan"
                            try:
                                resp = requests.post(
                                    scan_url, 
                                    json={"encodings": query_embedding.tolist()}, 
                                    headers=headers
                                )
                                print(f"[SCAN API] {resp.status_code} {resp.text}")
                            except Exception as ex:
                                print(f"[SCAN ERROR] {ex}")
                            
                            # Lưu attendance vào DB
                            db2 = mysql.connector.connect(
                                host="localhost",
                                user="root",
                                password="12345",
                                database="attendance_db"
                            )
                            cursor2 = db2.cursor()
                            from datetime import datetime
                            now = datetime.now()
                            cursor2.execute(
                                "INSERT INTO attendance_records (employee_id, check_in_time, status) VALUES (%s, %s, %s)",
                                (best_match['id'], now, 'present')
                            )
                            db2.commit()
                            cursor2.close()
                            db2.close()
                            
                            scanned = True
                        else:
                            self.label.setText(f"❌ Không nhận diện được (confidence: {best_similarity*100:.1f}%)")
                            scanned = True
                            
                    except Exception as e:
                        print(f"[ERROR] {e}")
                        self.label.setText(f"Lỗi nhận diện: {e}")
                        scanned = True
                
                QApplication.processEvents()
                
        else:
            self.camera_running = False
            self.cam_btn.setText("Bật Camera")
            self.label.setText("Camera đã tắt.")
            if self.cap:
                self.cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceIDApp()
    window.show()
    sys.exit(app.exec())
