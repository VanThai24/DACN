
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
        # Lấy class_names từ database (photo_path)
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="attendance_db"
        )
        cursor = db.cursor()
        cursor.execute("SELECT name, photo_path FROM employees ORDER BY id ASC")
        employee_rows = cursor.fetchall()
        class_names = [row[1] for row in employee_rows]  # photo_path
        employee_names = [row[0] for row in employee_rows]  # name
        cursor.close()
        db.close()

        # Lấy JWT token cho user (ví dụ dùng phone làm username, mật khẩu mặc định 123456)
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
            import numpy as np
            import os
            from tensorflow.keras.utils import img_to_array
            model_path = os.path.join(os.path.dirname(__file__), '../AI/faceid_model_tf.h5')
            model = tf.keras.models.load_model(model_path)
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
                # Dùng OpenCV để phát hiện khuôn mặt
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                if len(faces) > 0 and not scanned:
                    self.label.setText("Đã phát hiện khuôn mặt, đang xác thực bằng AI...")
                    (x, y, w, h) = faces[0]
                    face_img = rgb_frame[y:y+h, x:x+w]
                    try:
                        # Tiền xử lý ảnh khuôn mặt - cắt thành 3 vùng: mắt, mũi, miệng
                        h1 = int(h * 0.35)  # vùng mắt (trên)
                        h2 = int(h * 0.65)  # vùng mũi (giữa)
                        # Vùng mắt
                        eye_img = face_img[0:h1, :]
                        # Vùng mũi
                        nose_img = face_img[h1:h2, :]
                        # Vùng miệng
                        mouth_img = face_img[h2:h, :]
                        regions = [face_img, eye_img, nose_img, mouth_img]
                        preds_list = []
                        for region in regions:
                            if region.shape[0] < 10 or region.shape[1] < 10:
                                continue
                            region_resized = cv2.resize(region, (128, 128))
                            region_array = np.array(region_resized) / 255.0
                            region_array = np.expand_dims(region_array, axis=0)
                            preds = model.predict(region_array)
                            preds_list.append(preds[0])
                        if not preds_list:
                            self.label.setText("Không nhận diện được khuôn mặt (ảnh quá nhỏ hoặc lỗi cắt vùng)")
                            scanned = True
                            return
                        # Trung bình xác suất các vùng
                        avg_preds = np.mean(preds_list, axis=0)
                        pred_idx = np.argmax(avg_preds)
                        confidence = avg_preds[pred_idx]
                        threshold = 0.8  # Ngưỡng xác suất, tăng để giảm nhận diện sai
                        if confidence >= threshold and 0 <= pred_idx < len(employee_names):
                            emp_name = employee_names[pred_idx]
                            self.label.setText(f"Điểm danh thành công cho nhân viên: {emp_name}")
                            # Gửi embedding lên backend qua API /scan kèm JWT
                            import requests
                            embedding = avg_preds.tolist()
                            headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
                            scan_url = "http://localhost:8000/api/faceid/scan"
                            try:
                                resp = requests.post(scan_url, json={"encodings": embedding}, headers=headers)
                                print("[SCAN API]", resp.status_code, resp.text)
                            except Exception as ex:
                                print(f"[SCAN ERROR] {ex}")
                            db2 = mysql.connector.connect(
                                host="localhost",
                                user="root",
                                password="12345",
                                database="attendance_db"
                            )
                            cursor2 = db2.cursor()
                            # Lấy id nhân viên tương ứng
                            emp_id = None
                            cursor2.execute("SELECT id FROM employees WHERE name = %s LIMIT 1", (emp_name,))
                            result = cursor2.fetchone()
                            if result:
                                emp_id = result[0]
                                from datetime import datetime
                                now = datetime.now()
                                # Lấy thông tin bổ sung cho attendance_records
                                photo_path = class_names[pred_idx] if 0 <= pred_idx < len(class_names) else None
                                from datetime import time
                                shift_date = now.date()
                                start_time = now.time()
                                # Luôn dùng device_id là id server (ví dụ: 1)
                                device_id = 1

                                # Kiểm tra đã có ca làm hôm nay chưa (shifts)
                                cursor2.execute("SELECT id FROM shifts WHERE employee_id=%s AND date=%s", (emp_id, shift_date))
                                shift_row = cursor2.fetchone()
                                if shift_row:
                                    # Đã có ca hôm nay, không nhận diện/lưu thêm
                                    self.label.setText(f"Bạn đã điểm danh ca hôm nay!")
                                else:
                                    # Nếu chưa có ca làm hôm nay => check-in
                                    if start_time < time(11, 30):
                                        end_time = time(11, 30)
                                    else:
                                        end_time = time(16, 30)
                                    cursor2.execute(
                                        "INSERT INTO shifts (employee_id, date, start_time, end_time) VALUES (%s, %s, %s, %s)",
                                        (emp_id, shift_date, start_time, end_time)
                                    )
                                    status = 'checked_in'
                                    cursor2.execute(
                                        "INSERT INTO attendance_records (employee_id, timestamp_in, status, photo_path, device_id) VALUES (%s, %s, %s, %s, %s)",
                                        (emp_id, now, status, photo_path, device_id)
                                    )
                                db2.commit()
                            cursor2.close()
                            db2.close()
                        else:
                            self.label.setText("Không nhận diện được khuôn mặt hoặc độ tin cậy thấp.")
                    except Exception as e:
                        self.label.setText(f"Lỗi AI: {e}")
                    scanned = True
                elif len(faces) == 0:
                    scanned = False
                key = cv2.waitKey(1)
                if key == 27:
                    self.camera_running = False
                    break
            self.cap.release()
            cv2.destroyAllWindows()
            self.cam_btn.setText("Bật Camera")
            self.label.setText("Camera đã tắt.")
        else:
            self.camera_running = False
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.cam_btn.setText("Bật Camera")
            self.label.setText("Camera đã tắt.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceIDApp()
    window.show()
    sys.exit(app.exec())
