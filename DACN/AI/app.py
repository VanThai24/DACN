from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import sqlite3
from db import init_db

app = Flask(__name__)
import io
# Khởi tạo DB ngay khi app start, không dùng decorator để tránh lỗi Flask mới
init_db()
# API: Thêm khuôn mặt mới
@app.route('/add_face', methods=['POST'])
def add_face():
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'reason': 'Image and name required'}), 400
    file = request.files['image']
    name = request.form['name']
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image
    import io
    try:
        img_bytes = file.read()
        img = image.load_img(io.BytesIO(img_bytes), target_size=(128, 128))
    except Exception as e:
        app.logger.error(f"Cannot open image: {e}")
        return jsonify({'success': False, 'reason': f'Cannot open image: {e}'})
    try:
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        import os
        model_path = os.path.join(os.path.dirname(__file__), 'faceid_model_tf.h5')
        full_model = tf.keras.models.load_model(model_path)
        
        # Predict model đầy đủ trước để build
        _ = full_model.predict(img_array, verbose=0)
        
        # Sử dụng Sequential layer slicing thay vì tf.keras.Model
        from tensorflow.keras.models import Sequential
        embedding_layers = full_model.layers[:-1]  # Bỏ layer classification cuối
        partial_model = Sequential(embedding_layers)
        
        embedding = partial_model.predict(img_array, verbose=0)[0]
        embedding_bytes = embedding.astype(np.float64).tobytes()
        import base64
        embedding_b64 = base64.b64encode(embedding_bytes).decode("utf-8")
        
        from db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Kiểm tra xem employee đã tồn tại chưa
            cursor.execute('SELECT id FROM employees WHERE name = %s', (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update face_embedding cho employee hiện tại
                cursor.execute('UPDATE employees SET face_embedding = %s WHERE name = %s', 
                             (embedding_bytes, name))
            else:
                # Tạo employee mới với face_embedding  
                cursor.execute('''INSERT INTO employees 
                              (name, face_embedding, department, role, is_locked) 
                              VALUES (%s, %s, %s, %s, %s)''', 
                             (name, embedding_bytes, 'Unknown', 'employee', 0))
            
            conn.commit()
            return jsonify({
                'success': True, 
                'message': 'Face added successfully', 
                'name': name,
                'embedding_size': len(embedding),
                'embedding_b64': embedding_b64
            })
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Model or DB error: {e}")
        return jsonify({'success': False, 'reason': f'Model or DB error: {e}'})

# API: Xóa khuôn mặt theo id (xóa face_embedding, không xóa employee)
@app.route('/delete_face', methods=['DELETE'])
def delete_face():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'success': False, 'reason': 'ID required'}), 400
    
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Chỉ xóa face_embedding, không xóa employee
        cursor.execute('UPDATE employees SET face_embedding = NULL WHERE id = %s', (data['id'],))
        conn.commit()
        return jsonify({'success': True, 'message': 'Face deleted'})
    finally:
        cursor.close()
        conn.close()

# API: Sửa tên khuôn mặt theo id
@app.route('/update_face', methods=['PUT'])
def update_face():
    data = request.get_json()
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({'success': False, 'reason': 'ID and new name required'}), 400
    
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update tên trong table employees
        cursor.execute('UPDATE employees SET name = %s WHERE id = %s', (data['name'], data['id']))
        conn.commit()
        return jsonify({'success': True, 'message': 'Face updated'})
    finally:
        cursor.close()
        conn.close()

# API: Lấy danh sách khuôn mặt
@app.route('/faces', methods=['GET'])
def list_faces():
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Lấy employees có face_embedding
        cursor.execute('SELECT id, name FROM employees WHERE face_embedding IS NOT NULL')
        faces = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        return jsonify({'success': True, 'faces': faces})
    finally:
        cursor.close()
        conn.close()


def get_all_embeddings():
    """
    Lấy embeddings từ table employees trong MySQL database
    face_embedding là BLOB chứa numpy array
    Returns: list of (id, name, embedding) tuples
    """
    from db import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Đọc từ table employees
        cursor.execute('SELECT id, name, face_embedding FROM employees WHERE face_embedding IS NOT NULL')
        data = cursor.fetchall()
        
        embeddings = []
        for emp_id, name, embedding_blob in data:
            if embedding_blob:
                try:
                    # Embedding là bytes, convert sang numpy array
                    embedding = np.frombuffer(embedding_blob, dtype=np.float64)
                    if len(embedding) == 0:
                        # Thử float32 nếu float64 không hoạt động
                        embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    if len(embedding) > 0:
                        embeddings.append((emp_id, name, embedding))
                except Exception as e:
                    app.logger.warning(f"Cannot decode embedding for {name}: {e}")
                    continue
        
        return embeddings
    finally:
        cursor.close()
        conn.close()

@app.route('/scan', methods=['POST'])
def scan_face():
    if 'image' not in request.files:
        return jsonify({'success': False, 'reason': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    # Sử dụng TensorFlow model để extract embedding (giống /add_face)
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image
    import io
    
    try:
        # Load và preprocess image
        img_bytes = file.read()
        img = image.load_img(io.BytesIO(img_bytes), target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Load TensorFlow model
        import os
        model_path = os.path.join(os.path.dirname(__file__), 'faceid_model_tf.h5')
        full_model = tf.keras.models.load_model(model_path)
        
        # Predict và extract embedding
        _ = full_model.predict(img_array, verbose=0)
        from tensorflow.keras.models import Sequential
        embedding_layers = full_model.layers[:-1]
        partial_model = Sequential(embedding_layers)
        query_embedding = partial_model.predict(img_array, verbose=0)[0]
        
    except Exception as e:
        return jsonify({'success': False, 'reason': f'Image processing error: {e}'}), 400
    embeddings = get_all_embeddings()
    print(f"[DEBUG] Loaded {len(embeddings)} embeddings from database")
    min_dist = float('inf')  # Start with infinity
    best_id = None
    best_name = None
    
    # Convert query to float64 for comparison
    query_float64 = query_embedding.astype(np.float64)
    
    for emp_id, name, db_embedding in embeddings:
        dist = np.linalg.norm(db_embedding - query_float64)
        print(f"[DEBUG] {name} (ID {emp_id}): distance = {dist:.4f}")
        if dist < min_dist:
            min_dist = dist
            best_id = emp_id
            best_name = name
    
    print(f"[DEBUG] Best match: {best_name} (ID {best_id}) with distance {min_dist:.4f}")
    threshold = 10.0  # Threshold for TensorFlow model embeddings
    if min_dist < threshold:
        return jsonify({'success': True, 'result': 'Match', 'id': best_id, 'name': best_name, 'distance': float(min_dist)})
    else:
        return jsonify({'success': False, 'result': 'No match', 'distance': float(min_dist), 'reason': 'Face not recognized'})


@app.route('/')
def index():
    return "FaceID API is running. Use /scan to POST an image."

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
