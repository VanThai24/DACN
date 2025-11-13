"""
Flask API cho FaceID - Phiên bản cải tiến
Sử dụng Cosine Similarity thay vì Euclidean Distance
Độ chính xác cao hơn nhiều
"""

from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Sequential
import io
import os
import base64
from db import init_db, get_db_connection

app = Flask(__name__)

# Khởi tạo DB
init_db()

# Custom function cho L2 normalization (giống trong training)
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# Load model một lần khi start app
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'faceid_model_tf_best.h5')
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'faceid_model_tf.h5')

print(f"Loading model from: {MODEL_PATH}")
# Load với custom_objects cho Lambda layer
FULL_MODEL = tf.keras.models.load_model(MODEL_PATH, 
                                        custom_objects={'l2_normalize_func': l2_normalize_func})

# Build embedding model (bỏ classification layer)
# Layer embedding_normalized là layer cuối trước classification
embedding_model = tf.keras.Model(
    inputs=FULL_MODEL.input,
    outputs=FULL_MODEL.get_layer('embedding_normalized').output
)

print(f"✓ Model loaded successfully")
print(f"✓ Embedding size: {embedding_model.output_shape[-1]}")


def extract_embedding(img_bytes):
    """
    Extract embedding từ image bytes
    Returns: normalized embedding vector
    """
    try:
        img = image.load_img(io.BytesIO(img_bytes), target_size=(160, 160))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        embedding = embedding_model.predict(img_array, verbose=0)[0]
        return embedding
    except Exception as e:
        raise Exception(f"Cannot extract embedding: {e}")


def cosine_similarity(embedding1, embedding2):
    """
    Tính cosine similarity giữa 2 embeddings
    Returns: similarity score (0-1, càng cao càng giống)
    """
    # Embeddings đã được L2 normalized, nên cosine similarity = dot product
    return np.dot(embedding1, embedding2)


def cosine_distance(embedding1, embedding2):
    """
    Tính cosine distance (1 - similarity)
    Returns: distance (0-2, càng thấp càng giống)
    """
    return 1.0 - cosine_similarity(embedding1, embedding2)


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
            'update_face': 'PUT /update_face (id, name)'
        }
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
