from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import sqlite3
from db import DB_PATH, init_db

app = Flask(__name__)
import io
@app.before_first_request
def setup_db():
    init_db()
# API: Thêm khuôn mặt mới
@app.route('/add_face', methods=['POST'])
def add_face():
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'reason': 'Image and name required'}), 400
    file = request.files['image']
    name = request.form['name']
    img = face_recognition.load_image_file(file)
    face_locations = face_recognition.face_locations(img)
    if not face_locations:
        return jsonify({'success': False, 'reason': 'No face found'}), 400
    if len(face_locations) > 1:
        return jsonify({'success': False, 'reason': 'Multiple faces detected'}), 400
    encodings = face_recognition.face_encodings(img, known_face_locations=face_locations)
    if not encodings:
        return jsonify({'success': False, 'reason': 'Face encoding failed'}), 400
    embedding = encodings[0].astype(np.float64).tobytes()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO faces (name, embedding) VALUES (?, ?)', (name, embedding))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Face added successfully'})

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
