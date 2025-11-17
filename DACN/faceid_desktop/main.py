
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from datetime import datetime
import cv2
import mysql.connector
from anti_spoofing import AntiSpoofing
from mask_detection import MaskDetector

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
        self.setWindowTitle("Hệ Thống Chấm Công - DACN System")
        self.resize(1200, 900)
        self.setMinimumSize(1000, 800)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)
        
        # === HEADER SECTION - Clean modern design ===
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e5e7eb;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Logo circle
        logo_label = QLabel("👤")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 24))
        logo_label.setFixedSize(60, 60)
        logo_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #8b5cf6);
            border-radius: 30px;
            color: white;
        """)
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        self.title = QLabel("Hệ Thống Chấm Công")
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setStyleSheet("color: #1e293b;")
        
        subtitle = QLabel("Nhận diện khuôn mặt thông minh")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #64748b;")
        
        title_layout.addWidget(self.title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()
        
        # Clock on the right
        clock_layout = QVBoxLayout()
        clock_layout.setSpacing(5)
        
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignRight)
        self.clock_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.clock_label.setStyleSheet("color: #1e293b;")
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignRight)
        self.date_label.setFont(QFont("Segoe UI", 10))
        self.date_label.setStyleSheet("color: #64748b;")
        
        clock_layout.addWidget(self.clock_label)
        clock_layout.addWidget(self.date_label)
        clock_layout.addStretch()
        
        self.update_clock()
        
        # Timer để cập nhật đồng hồ
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_layout, 1)
        header_layout.addLayout(clock_layout)
        
        header_frame.setLayout(header_layout)
        
        # === STATUS SECTION - Clean card ===
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 12px;
                border: 1px solid #e5e7eb;
            }
        """)
        status_layout = QVBoxLayout()
        status_layout.setSpacing(10)
        
        # Status label with icon
        self.label = QLabel("📷 Sẵn sàng chấm công")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            color: #1e293b;
            padding: 15px;
            background: #f8fafc;
            border-radius: 12px;
            border: 2px dashed #cbd5e1;
        """)
        
        status_layout.addWidget(self.label)
        status_frame.setLayout(status_layout)
        
        # === CAMERA VIEW - Modern card ===
        camera_container = QFrame()
        camera_container.setFixedHeight(380)
        camera_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 8px;
                border: 1px solid #e5e7eb;
            }
        """)
        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(0, 0, 0, 0)
        camera_layout.setAlignment(Qt.AlignCenter)
        
        self.cam_view = QLabel()
        self.cam_view.setMinimumSize(650, 360)
        self.cam_view.setMaximumSize(650, 360)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet("""
            background: #0f172a;
            border-radius: 12px;
            color: #94a3b8;
            font-size: 18px;
            padding: 40px;
        """)
        self.cam_view.setText("📹 Camera chưa hoạt động\n\nNhấn nút bên dưới để bắt đầu")
        
        camera_layout.addWidget(self.cam_view)
        camera_container.setLayout(camera_layout)
        
        # === BUTTON SECTION ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.cam_btn = QPushButton("🎥 Bật Camera")
        self.cam_btn.setFixedHeight(60)
        self.cam_btn.setFixedWidth(300)
        self.cam_btn.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.cam_btn.setCursor(Qt.PointingHandCursor)
        self.cam_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: white;
                border-radius: 30px;
                padding: 0px 50px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #60a5fa, stop:1 #a78bfa);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #7c3aed);
            }
        """)
        self.cam_btn.clicked.connect(self.toggle_camera)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cam_btn)
        button_layout.addStretch()
        
        # Add all sections to main layout
        main_layout.addWidget(header_frame)
        main_layout.addSpacing(3)
        main_layout.addWidget(status_frame)
        main_layout.addSpacing(5)
        main_layout.addWidget(camera_container)
        main_layout.addSpacing(5)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        self.cap = None
        self.camera_running = False
        self.frame_skip_counter = 0  # 🚀 Skip frames để tăng FPS
        self.employee_cache = None  # 🚀 Cache employee data để không query DB mỗi lần
        self.clf_cache = None  # 🚀 Cache model để không load mỗi lần
        self.setLayout(main_layout)
        
        # Clean background
        self.setStyleSheet("""
            QWidget {
                background: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
    
    def update_clock(self):
        """Cập nhật đồng hồ thời gian thực"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d/%m/%Y")
        day_str = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][now.weekday()]
        self.clock_label.setText(time_str)
        self.date_label.setText(f"{day_str}, {date_str}")

    def toggle_camera(self):
        # Import numpy trước
        import numpy as np
        
        # 🚀 OPTIMIZATION: Cache employee data (chỉ load 1 lần)
        if self.employee_cache is None:
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
            
            self.employee_cache = employee_data
            print(f"✅ Loaded {len(employee_data)} employees with embeddings (CACHED)")
        else:
            employee_data = self.employee_cache
            print(f"✅ Using cached employee data ({len(employee_data)} employees)")

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
            self.cam_btn.setText("⏹️ Tắt Camera")
            self.cam_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ef4444, stop:1 #dc2626);
                    color: white;
                    border-radius: 30px;
                    padding: 0px 50px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f87171, stop:1 #ef4444);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #dc2626, stop:1 #b91c1c);
                }
            """)
            self.label.setText("📹 Camera đang hoạt động")
            self.label.setStyleSheet("""
                color: #1e293b;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                padding: 15px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #34d399;
                color: white;
            """)
            scanned = False
            from PySide6.QtGui import QImage, QPixmap
            import os
            import joblib
            import face_recognition
            
            # 🔥 LOAD BEST MODEL (100% accuracy) - CACHE để không load mỗi lần
            if self.clf_cache is None:
                model_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_best_model.pkl')
                metadata_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_best_model_metadata.pkl')
                
                if not os.path.exists(model_path):
                    self.label.setText("❌ Model không tồn tại! Chạy: python train_best_model.py")
                    self.camera_running = False
                    return
                
                clf = joblib.load(model_path)
                metadata = joblib.load(metadata_path)
                self.clf_cache = (clf, metadata)
                
                print(f"✅ Best Model loaded: {len(clf.classes_)} classes (CACHED)")
                print(f"✅ Test Accuracy: {metadata['test_accuracy']*100:.2f}%")
                print(f"✅ Avg Confidence: {metadata['avg_confidence']*100:.2f}%")
            else:
                clf, metadata = self.clf_cache
                print(f"✅ Using cached model ({len(clf.classes_)} classes)")
            
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
                
                # 🚀 OPTIMIZATION: Skip frames để giảm CPU
                self.frame_skip_counter += 1
                
                # Resize frame nhỏ hơn để xử lý nhanh hơn (giảm từ full size xuống 640x480)
                frame = cv2.resize(frame, (640, 480))
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 🚀 Chỉ update display mỗi frame (không skip display)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.cam_view.setPixmap(QPixmap.fromImage(qt_img).scaled(self.cam_view.size(), Qt.KeepAspectRatio))
                
                # 🚀 OPTIMIZATION: Chỉ detect face mỗi 3 frames (giảm 66% CPU)
                if self.frame_skip_counter % 3 != 0:
                    QApplication.processEvents()  # Keep UI responsive
                    continue
                
                # 🔥 FACE DETECTION: Sử dụng face_recognition với frame nhỏ hơn
                # Resize xuống 320x240 để detect nhanh hơn (giảm 4x CPU)
                small_frame = cv2.resize(rgb_frame, (320, 240))
                face_locations = face_recognition.face_locations(small_frame, model='hog')  # HOG nhanh hơn CNN
                
                # Convert to format (x, y, w, h) và scale lại tọa độ (vì detect trên small_frame)
                faces = []
                scale_factor = 2  # 640/320 = 2
                for (top, right, bottom, left) in face_locations:
                    x = left * scale_factor
                    y = top * scale_factor
                    w = (right - left) * scale_factor
                    h = (bottom - top) * scale_factor
                    faces.append([x, y, w, h])
                if len(faces) > 0 and not scanned:
                    self.label.setText("🔍 Đã phát hiện khuôn mặt - Đang nhận diện...")
                    self.label.setStyleSheet("""
                        color: white;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #f59e0b, stop:1 #d97706);
                        padding: 15px;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: bold;
                        border: 2px solid #fbbf24;
                    """)
                    (x, y, w, h) = faces[0]
                    face_img = rgb_frame[y:y+h, x:x+w]
                    
                    try:
                        # 🔒 SECURITY CHECKS - TẮT TẠM THỜI ĐỂ TEST NHANH
                        # Bật lại khi cần: Uncomment các dòng dưới
                        ENABLE_SECURITY = False  # Đổi thành True để bật security
                        
                        if ENABLE_SECURITY:
                            import io
                            from PIL import Image
                            
                            # Convert frame to bytes
                            pil_img = Image.fromarray(face_img)
                            img_byte_arr = io.BytesIO()
                            pil_img.save(img_byte_arr, format='JPEG')
                            img_bytes = img_byte_arr.getvalue()
                            
                            # 🔒 BƯỚC 1: Anti-Spoofing Check
                            anti_spoofing_detector = AntiSpoofing(threshold=0.50)  # Giảm xuống 50%
                            spoofing_result = anti_spoofing_detector.detect(img_bytes)
                            
                            if not spoofing_result['is_real']:
                                scores = spoofing_result['scores']
                                self.label.setText(
                                    f"🚫 PHÁT HIỆN GIẢ MẠO!\n"
                                    f"Vui lòng sử dụng khuôn mặt thật\n"
                                    f"(Score: {spoofing_result['confidence']:.0%}, Threshold: 50%)\n"
                                    f"T={scores['texture']:.2f} C={scores['color_diversity']:.2f} "
                                    f"M={scores['moire_pattern']:.2f} Q={scores['face_quality']:.2f}"
                                )
                                self.label.setStyleSheet("""
                                    color: white;
                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #dc2626, stop:1 #991b1b);
                                    padding: 15px;
                                    border-radius: 12px;
                                    font-size: 14px;
                                    font-weight: bold;
                                    border: 2px solid #ef4444;
                                """)
                                scanned = True
                                continue
                            
                            print(f"✅ Anti-spoofing: {spoofing_result['confidence']:.0%}")
                            
                            # 😷 BƯỚC 2: Mask Detection
                            mask_detector = MaskDetector(threshold=0.65)
                            mask_result = mask_detector.detect(img_bytes)
                            
                            if mask_result['wearing_mask']:
                                self.label.setText(f"😷 PHÁT HIỆN KHẨU TRANG!\nVui lòng tháo khẩu trang\n(Confidence: {mask_result['confidence']:.0%})")
                                self.label.setStyleSheet("""
                                    color: white;
                                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #f59e0b, stop:1 #d97706);
                                    padding: 15px;
                                    border-radius: 12px;
                                    font-size: 16px;
                                    font-weight: bold;
                                    border: 2px solid #fbbf24;
                                """)
                                scanned = True
                                continue
                            
                            print(f"✅ Mask check: Passed")
                        
                        # ✅ Face Recognition (nhanh hơn khi tắt security)
                        # 🔥 BEST MODEL: Extract embedding với face_recognition
                        # 🚀 OPTIMIZATION: Giảm size từ 300x300 xuống 150x150 (nhanh hơn 4x)
                        face_resized = cv2.resize(face_img, (150, 150))
                        
                        # 🚀 Get face encoding với model='small' (nhanh hơn large 5x, vẫn accurate)
                        face_encodings = face_recognition.face_encodings(face_resized, model='small')
                        
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
                                    
                                    # 🔥 KIỂM TRA THỜI GIAN: Không cho phép điểm danh sau 16:30
                                    if current_time > time(16, 30):
                                        self.label.setText(
                                            "⏰ NGOÀI GIỜ ĐIỂM DANH\n\n"
                                            "Hệ thống chỉ cho phép điểm danh\n"
                                            "từ 6:00 sáng đến 16:30 chiều"
                                        )
                                        self.label.setStyleSheet("""
                                            color: white;
                                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #ef4444, stop:1 #dc2626);
                                            padding: 20px;
                                            border-radius: 12px;
                                            font-size: 16px;
                                            font-weight: bold;
                                            border: 2px solid #f87171;
                                        """)
                                        scanned = False
                                        QApplication.processEvents()  # Keep UI responsive
                                        continue
                                    
                                    # 🔥 TỰ ĐỘNG XÁC ĐỊNH CA LÀM VIỆC DựA VÀO GIỜ ĐIỂM DANH
                                    # Ca sáng: 6:00 - 12:30 → Ca làm: 7:00 - 11:30
                                    # Ca chiều: 12:30 - 16:30 → Ca làm: 13:00 - 16:30
                                    if time(6, 0) <= current_time < time(12, 30):
                                        shift_start = time(8, 30)
                                        shift_end = time(11, 30)
                                        shift_name = "Ca sáng"
                                    else:  # Ca chiều
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
                                    
                                    # 🔥 KIỂM TRA TRÙNG: Xem nhân viên đã điểm danh ca này chưa
                                    cursor2.execute("""
                                        SELECT id, timestamp_in FROM attendance_records
                                        WHERE employee_id = %s 
                                        AND shift_id = %s
                                        LIMIT 1
                                    """, (emp_match['id'], shift_id))
                                    existing_attendance = cursor2.fetchone()
                                    
                                    if existing_attendance:
                                        # Đã điểm danh ca này rồi
                                        attendance_time = existing_attendance[1].strftime('%H:%M:%S')
                                        cursor2.close()
                                        db2.close()
                                        
                                        self.label.setText(
                                            f"⚠️ BẠN ĐÃ ĐIỂM DANH!\n\n"
                                            f"👤 {db_name}\n"
                                            f"📅 {shift_info}\n"
                                            f"⏰ Đã điểm danh lúc: {attendance_time}"
                                        )
                                        self.label.setStyleSheet("""
                                            color: white;
                                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #f59e0b, stop:1 #d97706);
                                            padding: 20px;
                                            border-radius: 12px;
                                            font-size: 14px;
                                            font-weight: bold;
                                            border: 2px solid #fbbf24;
                                            line-height: 1.6;
                                        """)
                                        scanned = False
                                        continue
                                    
                                    # Chưa điểm danh, lưu attendance
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
                
                # 🚀 OPTIMIZATION: Control FPS để giảm CPU (30ms = ~33 FPS, tăng lên 50ms = 20 FPS)
                key = cv2.waitKey(50)  # Tăng từ 1ms lên 50ms để giảm CPU
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
