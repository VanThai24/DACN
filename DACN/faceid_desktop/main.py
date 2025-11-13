
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
import cv2
import mysql.connector

class FaceIDApp(QWidget):
    def get_jwt_token(self, username, password):
        import requests
        url = "http://localhost:8000/api/auth/login"
        data = {"username": username, "password": password}
        try:
            resp = requests.post(url, json=data)
            print(f"[JWT DEBUG] status={resp.status_code}, response={resp.text}")
            if resp.status_code == 200 and "access_token" in resp.json():
                print(f"[JWT TOKEN] {resp.json()['access_token']}")
                return resp.json()["access_token"]
        except Exception as ex:
            print(f"[JWT ERROR] {ex}")
        return None
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
        self.setWindowTitle("🎯 FaceID - Hệ Thống Điểm Danh")
        self.setFixedSize(800, 650)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)
        
        # Title với gradient
        self.title = QLabel("<h1 style='color:#1976d2; text-align:center; margin:0;'>🎯 Hệ Thống Điểm Danh FaceID</h1>")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; padding: 10px;")
        
        # Status label
        self.label = QLabel("📷 Camera đã tắt - Nhấn nút để bắt đầu")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 18px; 
            color: #666; 
            background: #f0f4f8;
            padding: 15px;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
        """)
        
        # Camera view với border đẹp hơn
        self.cam_view = QLabel()
        self.cam_view.setFixedSize(720, 400)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet("""
            background: #f8f9fa; 
            border-radius: 20px; 
            border: 3px solid #1976d2;
            padding: 5px;
        """)
        
        # Button với hover effect
        self.cam_btn = QPushButton("🎥 BẬT CAMERA")
        self.cam_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1976d2, stop:1 #1565c0);
                color: white; 
                padding: 15px 40px; 
                border-radius: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1565c0, stop:1 #0d47a1);
            }
            QPushButton:pressed {
                background: #0d47a1;
            }
        """)
        self.cam_btn.clicked.connect(self.toggle_camera)
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.cam_view, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)
        self.layout.addWidget(self.cam_btn)
        
        self.cap = None
        self.camera_running = False
        self.setLayout(self.layout)
        
        # Background gradient
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e3f2fd, stop:1 #bbdefb);
            }
        """)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def toggle_camera(self):
        # Import numpy trước
        import numpy as np
        
        # Lấy embeddings từ database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="attendance_db"
        )
        cursor = db.cursor()
        # 🔥 EMBEDDING MATCHING: Lấy tất cả nhân viên có embedding
        cursor.execute("""
            SELECT id, name, 
                   COALESCE(face_encoding, face_embedding) as encoding
            FROM employees 
            WHERE face_encoding IS NOT NULL OR face_embedding IS NOT NULL
        """)
        employees_db = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Parse embeddings
        employee_data = []
        for emp_id, name, encoding_blob in employees_db:
            if encoding_blob:
                # Blob là bytes, convert về numpy array
                encoding = np.frombuffer(encoding_blob, dtype=np.float32)
                employee_data.append({
                    'id': emp_id,
                    'name': name,
                    'embedding': encoding
                })
        
        print(f"✅ Loaded {len(employee_data)} employees with embeddings")

        # Lấy JWT token cho user
        # Bỏ qua login nếu bị rate limit
        jwt_token = None
        try:
            jwt_token = self.get_jwt_token("testuser", "123456")
        except:
            print("[INFO] Bỏ qua login, app vẫn chạy bình thường")

        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.label.setText("❌ Không mở được camera!")
                self.label.setStyleSheet("""
                    font-size: 18px; color: #d32f2f; background: #ffebee;
                    padding: 15px; border-radius: 12px; border: 2px solid #ef5350;
                """)
                return
            self.camera_running = True
            self.cam_btn.setText("⏹️ TẮT CAMERA")
            self.label.setText("✨ Camera đang hoạt động - Đưa khuôn mặt vào khung hình")
            self.label.setStyleSheet("""
                font-size: 18px; color: #2e7d32; background: #e8f5e9;
                padding: 15px; border-radius: 12px; border: 2px solid #66bb6a;
            """)
            scanned = False
            from PySide6.QtGui import QImage, QPixmap
            import os
            import joblib
            import face_recognition
            
            # 🔥 LOAD BEST MODEL (100% accuracy)
            model_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_best_model.pkl')
            metadata_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_best_model_metadata.pkl')
            
            if not os.path.exists(model_path):
                self.label.setText("❌ Model không tồn tại! Chạy: python train_best_model.py")
                self.camera_running = False
                return
            
            clf = joblib.load(model_path)
            metadata = joblib.load(metadata_path)
            
            print(f"✅ Best Model loaded: {len(clf.classes_)} classes")
            print(f"✅ Test Accuracy: {metadata['test_accuracy']*100:.2f}%")
            print(f"✅ Avg Confidence: {metadata['avg_confidence']*100:.2f}%")
            
            # 🔥 MAPPING: Tên trong model → Tên trong database
            name_mapping = {
                'Thai': 'Đặng Văn Thái',  # Model có 'Thai', DB có 'Đặng Văn Thái'
                # Thêm các mapping khác nếu cần:
                # 'Huy': 'Nguyễn Văn Huy',
                # 'Phong': 'Trần Phong',
            }
            print(f"✅ Name mapping: {name_mapping}")
            
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
                # 🔥 FACE DETECTION: Sử dụng face_recognition thay vì MTCNN/Haar
                face_locations = face_recognition.face_locations(rgb_frame)
                
                # Convert to format (x, y, w, h) như Haar Cascade
                faces = []
                for (top, right, bottom, left) in face_locations:
                    x = left
                    y = top
                    w = right - left
                    h = bottom - top
                    faces.append([x, y, w, h])
                if len(faces) > 0 and not scanned:
                    self.label.setText("Đã phát hiện khuôn mặt, đang xác thực bằng AI...")
                    (x, y, w, h) = faces[0]
                    face_img = rgb_frame[y:y+h, x:x+w]
                    
                    try:
                        # 🔥 BEST MODEL: Extract embedding với face_recognition (large model)
                        face_resized = cv2.resize(face_img, (300, 300))  # Resize for better detection
                        
                        # Get face encoding với model='large'
                        face_encodings = face_recognition.face_encodings(face_resized, model='large')
                        
                        if len(face_encodings) == 0:
                            self.label.setText("⚠️ Không extract được face encoding!")
                            scanned = True
                            continue
                        
                        query_embedding = face_encodings[0]
                        
                        # 🔥 PREDICT với Best Model
                        prediction = clf.predict([query_embedding])[0]
                        proba = clf.predict_proba([query_embedding])[0]
                        confidence = np.max(proba)
                        
                        # Get top 3 predictions
                        top_3_idx = np.argsort(proba)[::-1][:3]
                        top_3_names = [clf.classes_[i] for i in top_3_idx]
                        top_3_probs = [proba[i] for i in top_3_idx]
                        
                        print(f"\n🔍 Predictions:")
                        for i, (name, prob) in enumerate(zip(top_3_names, top_3_probs), 1):
                            print(f"   {i}. {name:<20} : {prob*100:.1f}%")
                        
                        # 🔥 GIẢM THRESHOLD = 30% (do model có ít data, confidence thấp)
                        # Sau khi thu thập đủ 30-50 ảnh/người, tăng lên 60-70%
                        THRESHOLD = 0.30
                        
                        if confidence >= THRESHOLD:
                            emp_name = prediction
                            confidence_pct = confidence * 100
                            
                            # 🔥 ÁP DỤNG NAME MAPPING
                            db_name = name_mapping.get(emp_name, emp_name)  # Dùng tên gốc nếu không có mapping
                            
                            # Tìm employee_id từ database (dùng db_name)
                            emp_match = next((e for e in employee_data if e['name'] == db_name), None)
                            
                            if emp_match:
                                # Lưu attendance vào DB
                                try:
                                    db2 = mysql.connector.connect(
                                        host="localhost",
                                        user="root",
                                        password="12345",
                                        database="attendance_db"
                                    )
                                    cursor2 = db2.cursor()
                                    
                                    from datetime import datetime, time
                                    now = datetime.now()
                                    device_id = 1
                                    current_time = now.time()
                                    current_date = now.date()
                                    
                                    # 🔥 TỰ ĐỘNG XÁC ĐỊNH CA LÀM VIỆC DựA VÀO GIỜ ĐIỂM DANH
                                    # Ca sáng: 6:00 - 12:30 → Ca làm: 7:00 - 11:30
                                    # Ca chiều: 12:30 - 23:59 → Ca làm: 13:00 - 16:30
                                    if time(6, 0) <= current_time < time(12, 30):
                                        shift_start = time(8, 30)
                                        shift_end = time(11, 30)
                                        shift_name = "Ca sáng"
                                    else:  # Ca chiều/tối
                                        shift_start = time(13, 30)
                                        shift_end = time(16, 30)
                                        shift_name = "Ca chiều"
                                    
                                    # Kiểm tra xem ca đã tồn tại chưa
                                    cursor2.execute("""
                                        SELECT id FROM shifts 
                                        WHERE employee_id = %s 
                                        AND DATE(date) = %s
                                        AND start_time = %s
                                        AND end_time = %s
                                        LIMIT 1
                                    """, (emp_match['id'], current_date, shift_start, shift_end))
                                    existing_shift = cursor2.fetchone()
                                    
                                    if existing_shift:
                                        shift_id = existing_shift[0]
                                        print(f"✅ Sử dụng ca có sẵn: {shift_name} (ID: {shift_id})")
                                    else:
                                        # Tạo ca mới
                                        cursor2.execute("""
                                            INSERT INTO shifts (employee_id, date, start_time, end_time)
                                            VALUES (%s, %s, %s, %s)
                                        """, (emp_match['id'], current_date, shift_start, shift_end))
                                        shift_id = cursor2.lastrowid
                                        print(f"✅ Tạo ca mới: {shift_name} (ID: {shift_id})")
                                    
                                    shift_info = f"{shift_name}: {shift_start.strftime('%H:%M')}-{shift_end.strftime('%H:%M')}"
                                    
                                    cursor2.execute("""
                                        INSERT INTO attendance_records 
                                        (employee_id, timestamp_in, status, device_id, shift_id)
                                        VALUES (%s, %s, %s, %s, %s)
                                    """, (emp_match['id'], now, 'present', device_id, shift_id))
                                    db2.commit()
                                    
                                    print(f"✅ ĐIỂM DANH THÀNH CÔNG: {db_name} (model: {emp_name}) - {now.strftime('%Y-%m-%d %H:%M:%S')} - {shift_info}")
                                    
                                    cursor2.close()
                                    db2.close()
                                    
                                    self.label.setText(f"✅ ĐIỂM DANH THÀNH CÔNG!\n{db_name}\n({confidence_pct:.1f}%) - {now.strftime('%H:%M:%S')}\n{shift_info}")
                                    self.label.setStyleSheet("""
                                        font-size: 22px; 
                                        color: #1b5e20; 
                                        background: #c8e6c9;
                                        padding: 20px;
                                        border-radius: 15px;
                                        border: 3px solid #4caf50;
                                        font-weight: bold;
                                    """)
                                    
                                except Exception as db_error:
                                    print(f"❌ DATABASE ERROR: {db_error}")
                                    self.label.setText(f"⚠️ Nhận diện: {db_name} ({confidence_pct:.1f}%)\nLỗi lưu DB!")
                                    self.label.setStyleSheet("""
                                        font-size: 18px; color: #e65100; background: #fff3e0;
                                        padding: 15px; border-radius: 12px; border: 2px solid #ff9800;
                                    """)
                                
                                # Gửi lên backend (optional)
                                try:
                                    import requests
                                    headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
                                    scan_url = "http://localhost:8000/api/faceid/scan"
                                    resp = requests.post(
                                        scan_url, 
                                        json={"encodings": query_embedding.tolist()}, 
                                        headers=headers,
                                        timeout=2
                                    )
                                    print(f"[SCAN API] {resp.status_code}")
                                except Exception as ex:
                                    print(f"[SCAN API ERROR] {ex} (không ảnh hưởng)")
                            else:
                                print(f"❌ KHÔNG TÌM THẤY: Model={emp_name}, DB lookup={db_name}")
                                self.label.setText(f"⚠️ Nhận diện: {emp_name} ({confidence_pct:.1f}%)\nKhông tìm thấy trong DB!")
                                self.label.setStyleSheet("""
                                    font-size: 18px; color: #e65100; background: #fff3e0;
                                    padding: 15px; border-radius: 12px; border: 2px solid #ff9800;
                                """)
                            
                            scanned = True
                        else:
                            # Show top prediction even if below threshold
                            confidence_pct = confidence * 100
                            self.label.setText(
                                f"❌ Không nhận diện được!\n"
                                f"Gần nhất: {prediction} ({confidence_pct:.1f}%)\n"
                                f"Cần ít nhất 30% confidence"
                            )
                            self.label.setStyleSheet("""
                                font-size: 18px; color: #c62828; background: #ffcdd2;
                                padding: 15px; border-radius: 12px; border: 2px solid #ef5350;
                            """)
                            scanned = True
                            
                    except Exception as e:
                        print(f"[ERROR] {e}")
                        self.label.setText(f"⚠️ Lỗi xử lý: {str(e)[:50]}")
                        self.label.setStyleSheet("""
                            font-size: 16px; color: #d32f2f; background: #ffebee;
                            padding: 15px; border-radius: 12px; border: 2px solid #ef5350;
                        """)
                        scanned = True
                        
                elif len(faces) == 0:
                    scanned = False
                    
                QApplication.processEvents()
                
                key = cv2.waitKey(1)
                if key == 27:
                    self.camera_running = False
                    break
            self.cap.release()
            cv2.destroyAllWindows()
            self.cam_btn.setText("🎥 BẬT CAMERA")
            self.label.setText("📷 Camera đã tắt - Nhấn nút để bắt đầu")
            self.label.setStyleSheet("""
                font-size: 18px; color: #666; background: #f0f4f8;
                padding: 15px; border-radius: 12px; border: 2px solid #e0e0e0;
            """)
        else:
            self.camera_running = False
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.cam_btn.setText("🎥 BẬT CAMERA")
            self.label.setText("📷 Camera đã tắt - Nhấn nút để bắt đầu")
            self.label.setStyleSheet("""
                font-size: 18px; color: #666; background: #f0f4f8;
                padding: 15px; border-radius: 12px; border: 2px solid #e0e0e0;
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceIDApp()
    window.show()
    sys.exit(app.exec())
