from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import sqlite3
from db import DB_PATH, init_db

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
        print(f"[DEBUG] file.filename={file.filename}, content_type={file.content_type}, content_length={file.content_length}")
        img_bytes = file.read()
        print(f"[DEBUG] img_bytes length={len(img_bytes)}")
        # Lưu file tạm để kiểm tra
        with open("debug_upload.jpg", "wb") as f:
            f.write(img_bytes)
        img = image.load_img(io.BytesIO(img_bytes), target_size=(128, 128))
    except Exception as e:
        print(f"[ERROR] Cannot open image: {e}")
        return jsonify({'success': False, 'reason': f'Cannot open image: {e}'})
    try:
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        import os
        model_path = os.path.join(os.path.dirname(__file__), 'faceid_model_tf.h5')
        model = tf.keras.models.load_model(model_path)
        embedding = model.predict(img_array)[0]
        # Log tự động kiểm tra embedding
        with open("embedding_debug.log", "a", encoding="utf-8") as f:
            f.write(f"name={name}, embedding_shape={embedding.shape}, embedding_sample={embedding[:5].tolist()}\n")
        embedding_bytes = embedding.astype(np.float64).tobytes()
        import base64
        embedding_b64 = base64.b64encode(embedding_bytes).decode("utf-8")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO faces (name, embedding) VALUES (?, ?)', (name, embedding_bytes))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Face added successfully', 'embedding_b64': embedding_b64})
    except Exception as e:
        print(f"[ERROR] Model or DB error: {e}")
        with open("embedding_debug.log", "a", encoding="utf-8") as f:
            f.write(f"name={name}, ERROR: {e}\n")
        return jsonify({'success': False, 'reason': f'Model or DB error: {e}'})

# API: Xóa khuôn mặt theo id
@app.route('/delete_face', methods=['DELETE'])
def delete_face():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'success': False, 'reason': 'ID required'}), 400
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM faces WHERE id = ?', (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Face deleted'})

# API: Sửa tên khuôn mặt theo id
@app.route('/update_face', methods=['PUT'])
def update_face():
    data = request.get_json()
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({'success': False, 'reason': 'ID and new name required'}), 400
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE faces SET name = ? WHERE id = ?', (data['name'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Face updated'})

# API: Lấy danh sách khuôn mặt
@app.route('/faces', methods=['GET'])
def list_faces():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM faces')
    faces = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'faces': faces})


def get_all_embeddings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, embedding FROM faces')
    data = c.fetchall()
    conn.close()
    embeddings = [(name, np.frombuffer(embedding, dtype=np.float64)) for name, embedding in data]
    return embeddings

@app.route('/scan', methods=['POST'])
def scan_face():
    if 'image' not in request.files:
        return jsonify({'success': False, 'reason': 'No image uploaded'}), 400
    file = request.files['image']
    img = face_recognition.load_image_file(file)
    face_locations = face_recognition.face_locations(img)
    if not face_locations:
        return jsonify({'success': False, 'reason': 'No face found'}), 400
    if len(face_locations) > 1:
        return jsonify({'success': False, 'reason': 'Multiple faces detected'}), 400
    # Kiểm tra chất lượng ảnh: đơn giản là kiểm tra kích thước khuôn mặt
    top, right, bottom, left = face_locations[0]
    face_width = right - left
    face_height = bottom - top
    if face_width < 60 or face_height < 60:
        return jsonify({'success': False, 'reason': 'Face too small or blurry'}), 400
    encodings = face_recognition.face_encodings(img, known_face_locations=face_locations)
    if not encodings:
        return jsonify({'success': False, 'reason': 'Face encoding failed'}), 400
    query_embedding = encodings[0]
    embeddings = get_all_embeddings()
    min_dist = 1.0
    best_name = None
    for name, db_embedding in embeddings:
        dist = np.linalg.norm(db_embedding - query_embedding)
        if dist < min_dist:
            min_dist = dist
            best_name = name
    threshold = 0.6
    if min_dist < threshold:
        return jsonify({'success': True, 'result': 'Match', 'name': best_name, 'distance': float(min_dist)})
    else:
        return jsonify({'success': False, 'result': 'No match', 'distance': float(min_dist), 'reason': 'Face not recognized'})


@app.route('/')
def index():
    return "FaceID API is running. Use /scan to POST an image."

if __name__ == '__main__':
    app.run(debug=True)
