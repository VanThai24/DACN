
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from datetime import datetime
import cv2
import mysql.connector

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
        self.setWindowTitle("FaceID - Hệ Thống Điểm Danh Thông Minh")
        self.resize(1000, 850)
        self.setMinimumSize(800, 700)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)
        
        # === HEADER SECTION ===
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:0.5 #1976D2, stop:1 #0D47A1);
                border-radius: 12px;
                padding: 12px;
            }
        """)
        header_layout = QVBoxLayout()
        
        # Title
        self.title = QLabel("🎯 HỆ THỐNG ĐIỂM DANH FACEID")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setStyleSheet("color: white; padding: 3px;")
        
        # Clock
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setFont(QFont("Segoe UI", 12))
        self.clock_label.setStyleSheet("color: #E3F2FD; padding: 2px;")
        self.update_clock()
        
        # Timer để cập nhật đồng hồ
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.clock_label)
        header_frame.setLayout(header_layout)
        
        # === INFO SECTION ===
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 2px solid #E0E0E0;
            }
        """)
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(10, 8, 10, 8)
        
        # Status label
        self.label = QLabel("📷 Sẵn sàng điểm danh - Nhấn nút để bắt đầu")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 12))
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            color: #616161;
            padding: 10px;
            background: #F5F5F5;
            border-radius: 8px;
        """)
        
        info_layout.addWidget(self.label)
        info_frame.setLayout(info_layout)
        
        # === CAMERA VIEW ===
        camera_container = QFrame()
        camera_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
                border-radius: 20px;
                border: 3px solid #2196F3;
                padding: 10px;
            }
        """)
        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cam_view = QLabel()
        self.cam_view.setMinimumSize(640, 400)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet("""
            background: #263238;
            border-radius: 12px;
            color: #78909C;
            font-size: 16px;
        """)
        self.cam_view.setText("📹 Camera chưa hoạt động")
        
        camera_layout.addWidget(self.cam_view)
        camera_container.setLayout(camera_layout)
        
        # === BUTTON SECTION ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cam_btn = QPushButton("🎥 BẬT CAMERA")
        self.cam_btn.setFixedHeight(55)
        self.cam_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.cam_btn.setCursor(Qt.PointingHandCursor)
        self.cam_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #2E7D32);
                color: white;
                border-radius: 15px;
                padding: 15px 40px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: #1B5E20;
            }
        """)
        self.cam_btn.clicked.connect(self.toggle_camera)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cam_btn)
        button_layout.addStretch()
        
        # Add all sections to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(info_frame)
        main_layout.addWidget(camera_container)
        main_layout.addLayout(button_layout)
        
        self.cap = None
        self.camera_running = False
        self.setLayout(main_layout)
        
        # Background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FAFAFA, stop:1 #ECEFF1);
            }
        """)
    
    def update_clock(self):
        """Cập nhật đồng hồ thời gian thực"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
        day_str = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][now.weekday()]
        self.clock_label.setText(f"📅 {day_str}, {date_str} | ⏰ {time_str}")

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
            self.cam_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F44336, stop:1 #C62828);
                    color: white;
                    border-radius: 15px;
                    padding: 15px 40px;
                    border: none;
                    font-weight: bold;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #EF5350, stop:1 #F44336);
                }
                QPushButton:pressed {
                    background: #B71C1C;
                }
            """)
            self.label.setText("✨ Camera đang hoạt động - Hãy nhìn thẳng vào camera")
            self.label.setStyleSheet("""
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #2E7D32);
                padding: 15px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
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
                    self.label.setText("🔍 Đã phát hiện khuôn mặt! Đang xác thực bằng AI...")
                    self.label.setStyleSheet("""
                        color: white;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #FF9800, stop:1 #F57C00);
                        padding: 15px;
                        border-radius: 10px;
                        font-size: 13px;
                        font-weight: bold;
                    """)
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
                                    
                                    self.label.setText(
                                        f"✅ ĐIỂM DANH THÀNH CÔNG!\n\n"
                                        f"👤 {db_name}\n"                                      
                                        f"⏰ Thời gian: {now.strftime('%H:%M:%S')}\n"
                                        f"📅 {shift_info}"
                                    )
                                    self.label.setStyleSheet("""
                                        color: white;
                                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #4CAF50, stop:1 #2E7D32);
                                        padding: 20px;
                                        border-radius: 10px;
                                        font-size: 14px;
                                        font-weight: bold;
                                        line-height: 1.6;
                                    """)
                                    
                                except Exception as db_error:
                                    print(f"❌ DATABASE ERROR: {db_error}")
                                    self.label.setText(
                                        f"⚠️ LỖI LƯU DỮ LIỆU\n\n"
                                        f"👤 Nhận diện: {db_name}\n"
                                        f"❌ Không thể lưu vào cơ sở dữ liệu"
                                    )
                                    self.label.setStyleSheet("""
                                        color: #BF360C;
                                        background: #FFE0B2;
                                        padding: 15px;
                                        border-radius: 10px;
                                        font-size: 13px;
                                        font-weight: bold;
                                        border: 2px solid #FF9800;
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
                                self.label.setText(
                                    f"⚠️ KHÔNG TÌM THẤY NHÂN VIÊN\n\n"
                                    f"👤 Nhận diện: {emp_name}\n"
                                    f"❌ Không có trong cơ sở dữ liệu"
                                )
                                self.label.setStyleSheet("""
                                    color: #BF360C;
                                    background: #FFE0B2;
                                    padding: 15px;
                                    border-radius: 10px;
                                    font-size: 13px;
                                    font-weight: bold;
                                    border: 2px solid #FF9800;
                                """)
                            
                            scanned = True
                        else:
                            # Show top prediction even if below threshold
                            confidence_pct = confidence * 100
                            self.label.setText(
                                f"❌ KHÔNG NHẬN DIỆN ĐƯỢC\n\n"
                                f"👤 Gần nhất: {prediction}\n"
                                f"⚠️ Yêu cầu tối thiểu: 30%"
                            )
                            self.label.setStyleSheet("""
                                color: white;
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #F44336, stop:1 #C62828);
                                padding: 15px;
                                border-radius: 10px;
                                font-size: 13px;
                                font-weight: bold;
                            """)
                            scanned = True
                            
                    except Exception as e:
                        print(f"[ERROR] {e}")
                        self.label.setText(
                            f"⚠️ LỖI XỬ LÝ\n\n"
                            f"❌ {str(e)[:100]}"
                        )
                        self.label.setStyleSheet("""
                            color: #C62828;
                            background: #FFCDD2;
                            padding: 15px;
                            border-radius: 10px;
                            font-size: 12px;
                            border: 2px solid #F44336;
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
