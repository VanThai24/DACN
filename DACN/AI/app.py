"""
Flask API cho FaceID - Best Model Version
Sử dụng Face Recognition (dlib) + SVM
Độ chính xác: 100%
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import io
import os
import base64
import pickle
import face_recognition
from PIL import Image
import mysql.connector
from datetime import datetime, time as dt_time

app = Flask(__name__)
CORS(app)  # Enable CORS cho mobile app

# 🔥 Load Best Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'faceid_best_model.pkl')
METADATA_PATH = os.path.join(os.path.dirname(__file__), 'faceid_best_model_metadata.pkl')

print(f"Loading Best Model from: {MODEL_PATH}")

with open(MODEL_PATH, 'rb') as f:
    clf = pickle.load(f)

with open(METADATA_PATH, 'rb') as f:
    metadata = pickle.load(f)

print(f"✓ Best Model loaded successfully")
print(f"✓ Test Accuracy: {metadata['test_accuracy']*100:.1f}%")
print(f"✓ Classes: {metadata['classes']}")

# Database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="attendance_db"
    )

def extract_embedding(img_bytes):
    """Extract face encoding sử dụng face_recognition"""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)
        
        face_encodings = face_recognition.face_encodings(img_array, model='large')
        
        if len(face_encodings) == 0:
            raise Exception("No face detected")
        
        return face_encodings[0]
    except Exception as e:
        raise Exception(f"Cannot extract embedding: {e}")


@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'model': 'Best Model (Face Recognition + SVM)',
        'accuracy': f"{metadata['test_accuracy']*100:.1f}%",
        'classes': metadata['classes']
    })


@app.route('/scan', methods=['POST'])
def scan_face():
    """
    Nhận diện khuôn mặt và tự động lưu attendance
    """
    try:
        # Get image
        if 'image' in request.files:
            img_bytes = request.files['image'].read()
        elif 'image' in request.json:
            img_bytes = base64.b64decode(request.json['image'])
        else:
            return jsonify({'success': False, 'reason': 'No image provided'}), 400
        
        # Extract embedding
        query_embedding = extract_embedding(img_bytes)
        
    except Exception as e:
        return jsonify({'success': False, 'reason': str(e)}), 400
    
    try:
        # Predict
        prediction = clf.predict([query_embedding])[0]
        proba = clf.predict_proba([query_embedding])[0]
        confidence = float(np.max(proba))
        
        # Name mapping
        name_mapping = {'Thai': 'Đặng Văn Thái'}
        db_name = name_mapping.get(prediction, prediction)
        
        # Get employee_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM employees WHERE name = %s', (db_name,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            db.close()
            return jsonify({
                'success': False,
                'reason': f'Employee {db_name} not found',
                'name': prediction,
                'confidence': confidence
            })
        
        emp_id = result[0]
        
        # Check threshold
        THRESHOLD = 0.30
        if confidence < THRESHOLD:
            cursor.close()
            db.close()
            return jsonify({
                'success': False,
                'reason': f'Confidence too low: {confidence*100:.1f}%',
                'employee_id': emp_id,
                'name': db_name,
                'confidence': confidence
            })
        
        # Tự động tạo ca và lưu attendance
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        
        # Xác định ca
        if dt_time(6, 0) <= current_time < dt_time(12, 30):
            shift_start = dt_time(7, 0)
            shift_end = dt_time(11, 30)
        else:
            shift_start = dt_time(13, 0)
            shift_end = dt_time(16, 30)
        
        # Kiểm tra ca đã tồn tại
        cursor.execute("""
            SELECT id FROM shifts 
            WHERE employee_id = %s 
            AND DATE(date) = %s
            AND start_time = %s
            AND end_time = %s
            LIMIT 1
        """, (emp_id, current_date, shift_start, shift_end))
        existing_shift = cursor.fetchone()
        
        if existing_shift:
            shift_id = existing_shift[0]
        else:
            cursor.execute("""
                INSERT INTO shifts (employee_id, date, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (emp_id, current_date, shift_start, shift_end))
            shift_id = cursor.lastrowid
        
        # 🔥 KIỂM TRA TRÙNG: Xem nhân viên đã điểm danh ca này chưa
        cursor.execute("""
            SELECT id, timestamp_in FROM attendance_records
            WHERE employee_id = %s 
            AND shift_id = %s
            LIMIT 1
        """, (emp_id, shift_id))
        existing_attendance = cursor.fetchone()
        
        if existing_attendance:
            # Đã điểm danh ca này rồi
            cursor.close()
            db.close()
            attendance_time = existing_attendance[1].strftime('%H:%M:%S')
            return jsonify({
                'success': False,
                'reason': 'already_checked_in',
                'message': f'Bạn đã điểm danh ca này lúc {attendance_time}',
                'employee_id': emp_id,
                'name': db_name,
                'attendance_time': attendance_time,
                'shift_id': shift_id
            })
        
        # Chưa điểm danh, lưu attendance
        cursor.execute("""
            INSERT INTO attendance_records 
            (employee_id, timestamp_in, status, device_id, shift_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (emp_id, now, 'present', 1, shift_id))
        db.commit()
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'employee_id': emp_id,
            'name': db_name,
            'confidence': confidence,
            'attendance_saved': True,
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'reason': str(e)}), 500


@app.route('/attendance/employee/<int:emp_id>', methods=['GET'])
def get_employee_attendance(emp_id):
    """
    API cho mobile app - Lấy lịch sử điểm danh của nhân viên
    """
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                a.id,
                a.employee_id,
                a.timestamp_in,
                a.status,
                s.start_time,
                s.end_time,
                s.date as shift_date
            FROM attendance_records a
            LEFT JOIN shifts s ON a.shift_id = s.id
            WHERE a.employee_id = %s
            ORDER BY a.timestamp_in DESC
            LIMIT 100
        """, (emp_id,))
        
        records = cursor.fetchall()
        
        # Convert datetime to ISO format cho JSON
        for r in records:
            if r['timestamp_in']:
                r['timestamp_in'] = r['timestamp_in'].isoformat()
            if r['shift_date']:
                r['shift_date'] = r['shift_date'].isoformat()
            if r['start_time']:
                r['start_time'] = str(r['start_time'])
            if r['end_time']:
                r['end_time'] = str(r['end_time'])
        
        cursor.close()
        db.close()
        
        return jsonify(records)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/employees', methods=['GET'])
def get_employees():
    """Lấy danh sách nhân viên"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, name, department, role FROM employees')
        employees = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(employees)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Lấy thông tin user bao gồm employee_id"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, username, employee_id, role FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
