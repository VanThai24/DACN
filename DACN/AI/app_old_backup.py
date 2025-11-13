"""
Flask API cho FaceID - Phiên bản Best Model
Sử dụng Face Recognition (dlib) + SVM Classifier
Độ chính xác: 100%
"""

from flask import Flask, request, jsonify
import numpy as np
import io
import os
import base64
import pickle
import face_recognition
from PIL import Image
from db import init_db, get_db_connection
import mysql.connector

app = Flask(__name__)

# Khởi tạo DB
init_db()

# 🔥 Load Best Model (SVM Classifier)
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
print(f"✓ Best params: {metadata['best_params']}")

def extract_embedding(img_bytes):
    """
    Extract embedding từ image bytes sử dụng face_recognition
    Returns: 128-dimensional face encoding
    """
    try:
        # Load image từ bytes
        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)
        
        # Extract face encoding với model='large' (99.38% accuracy)
        face_encodings = face_recognition.face_encodings(img_array, model='large')
        
        if len(face_encodings) == 0:
            raise Exception("No face detected in image")
        
        # Lấy face đầu tiên
        embedding = face_encodings[0]
        return embedding
    except Exception as e:
        raise Exception(f"Cannot extract embedding: {e}")



# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/add_face', methods=['POST'])
def add_face():
    """
    Thêm khuôn mặt mới vào database
    POST: image (file), name (form data)
    """
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'reason': 'Image and name required'}), 400
    
    file = request.files['image']
    name = request.form['name']
    
    try:
        # Extract embedding
        img_bytes = file.read()
        embedding = extract_embedding(img_bytes)
        
        # Convert to bytes để lưu vào DB
        embedding_bytes = embedding.astype(np.float32).tobytes()
        embedding_b64 = base64.b64encode(embedding_bytes).decode("utf-8")
        
        # Lưu vào database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Kiểm tra employee đã tồn tại chưa
            cursor.execute('SELECT id FROM employees WHERE name = %s', (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update face_embedding
                cursor.execute(
                    'UPDATE employees SET face_embedding = %s WHERE name = %s',
                    (embedding_bytes, name)
                )
                message = f'Updated face for {name}'
            else:
                # Tạo employee mới
                cursor.execute('''
                    INSERT INTO employees 
                    (name, face_embedding, department, role, is_locked) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, embedding_bytes, 'Unknown', 'employee', 0))
                message = f'Added new face for {name}'
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': message,
                'name': name,
                'embedding_size': len(embedding),
                'embedding_b64': embedding_b64
            })
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        app.logger.error(f"Error in add_face: {e}")
        return jsonify({'success': False, 'reason': str(e)}), 500


@app.route('/scan', methods=['POST'])
def scan_face():
    """
    Nhận diện khuôn mặt
    POST: image (file)
    Returns: best match với confidence score
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'reason': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    try:
        # Extract embedding từ ảnh upload
        img_bytes = file.read()
        query_embedding = extract_embedding(img_bytes)
        
    except Exception as e:
        app.logger.error(f"Cannot extract embedding: {e}")
        return jsonify({'success': False, 'reason': f'Image processing error: {e}'}), 400
    
    # Lấy tất cả embeddings từ database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name, face_embedding FROM employees WHERE face_embedding IS NOT NULL')
        data = cursor.fetchall()
        
        if not data:
            return jsonify({
                'success': False,
                'reason': 'No faces in database',
                'result': 'No match'
            })
        
        embeddings = []
        for emp_id, name, embedding_blob in data:
            if embedding_blob:
                try:
                    # Convert bytes to numpy array
                    db_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    if len(db_embedding) == len(query_embedding):
                        embeddings.append((emp_id, name, db_embedding))
                except Exception as e:
                    app.logger.warning(f"Cannot decode embedding for {name}: {e}")
        
        if not embeddings:
            return jsonify({
                'success': False,
                'reason': 'No valid embeddings in database',
                'result': 'No match'
            })
        
        print(f"[DEBUG] Loaded {len(embeddings)} embeddings from database")
        
        # Tìm best match bằng cosine similarity
        best_similarity = -1.0  # Start with -1 (worst possible)
        best_distance = 2.0  # Start with 2 (worst possible)
        best_id = None
        best_name = None
        
        for emp_id, name, db_embedding in embeddings:
            similarity = cosine_similarity(query_embedding, db_embedding)
            distance = cosine_distance(query_embedding, db_embedding)
            
            print(f"[DEBUG] {name} (ID {emp_id}): similarity = {similarity:.4f}, distance = {distance:.4f}")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_distance = distance
                best_id = emp_id
                best_name = name
        
        print(f"[DEBUG] Best match: {best_name} (ID {best_id})")
        print(f"[DEBUG] Similarity: {best_similarity:.4f}, Distance: {best_distance:.4f}")
        
        # Threshold cho cosine similarity (0.6 - 0.7 là tốt)
        SIMILARITY_THRESHOLD = 0.65  # Càng cao càng strict
        # Hoặc dùng distance threshold (< 0.4 là tốt)
        DISTANCE_THRESHOLD = 0.35
        
        if best_similarity >= SIMILARITY_THRESHOLD or best_distance <= DISTANCE_THRESHOLD:
            return jsonify({
                'success': True,
                'result': 'Match',
                'id': best_id,
                'name': best_name,
                'similarity': float(best_similarity),
                'distance': float(best_distance),
                'confidence': float(best_similarity * 100)
            })
        else:
            return jsonify({
                'success': False,
                'result': 'No match',
                'reason': 'Face not recognized',
                'best_similarity': float(best_similarity),
                'best_distance': float(best_distance),
                'threshold': SIMILARITY_THRESHOLD
            })
    
    finally:
        cursor.close()
        conn.close()


@app.route('/delete_face', methods=['DELETE'])
def delete_face():
    """Xóa face_embedding của employee"""
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'success': False, 'reason': 'ID required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE employees SET face_embedding = NULL WHERE id = %s', (data['id'],))
        conn.commit()
        return jsonify({'success': True, 'message': 'Face deleted'})
    finally:
        cursor.close()
        conn.close()


@app.route('/update_face', methods=['PUT'])
def update_face():
    """Cập nhật tên employee"""
    data = request.get_json()
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({'success': False, 'reason': 'ID and new name required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE employees SET name = %s WHERE id = %s', (data['name'], data['id']))
        conn.commit()
        return jsonify({'success': True, 'message': 'Face updated'})
    finally:
        cursor.close()
        conn.close()


@app.route('/faces', methods=['GET'])
def list_faces():
    """Lấy danh sách employees có face"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, name FROM employees WHERE face_embedding IS NOT NULL')
        faces = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify({'success': True, 'faces': faces})
    finally:
        cursor.close()
        conn.close()


@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'FaceID API v2.0 - Improved with Transfer Learning',
        'model': 'MobileNetV2 + L2 Normalization',
        'similarity_method': 'Cosine Similarity',
        'endpoints': {
            'scan': 'POST /scan (image)',
            'add_face': 'POST /add_face (image, name)',
            'faces': 'GET /faces',
            'delete_face': 'DELETE /delete_face (id)',
            'update_face': 'PUT /update_face (id, name)',
            'attendance': 'GET /attendance/employee/{id}'
        }
    })


# 📱 API CHO MOBILE APP
@app.route('/attendance/employee/<int:employee_id>', methods=['GET'])
def get_employee_attendance(employee_id):
    """Lấy lịch sử điểm danh của nhân viên (cho mobile app)"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Lấy attendance records kèm thông tin ca làm việc
        cursor.execute("""
            SELECT 
                a.id,
                a.employee_id,
                a.timestamp_in,
                a.status,
                a.shift_id,
                s.start_time,
                s.end_time,
                s.date as shift_date
            FROM attendance_records a
            LEFT JOIN shifts s ON a.shift_id = s.id
            WHERE a.employee_id = %s
            ORDER BY a.timestamp_in DESC
            LIMIT 100
        """, (employee_id,))
        
        records = cursor.fetchall()
        
        # Format dữ liệu cho mobile app
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'employee_id': record['employee_id'],
                'timestamp_in': record['timestamp_in'].strftime('%Y-%m-%d %H:%M:%S') if record['timestamp_in'] else None,
                'status': record['status'],
                'shift_id': record['shift_id'],
                'shift_start': str(record['start_time']) if record['start_time'] else None,
                'shift_end': str(record['end_time']) if record['end_time'] else None,
                'shift_date': record['shift_date'].strftime('%Y-%m-%d') if record['shift_date'] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)  # Port 8000 cho mobile app
