import face_recognition
import numpy as np
import sqlite3
from db import DB_PATH
import sys

# Usage: python add_face.py <image_path> <name>
def add_face(image_path, name):
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    if not encodings:
        print('No face found in image.')
        return
    embedding = encodings[0]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO faces (name, embedding) VALUES (?, ?)', (name, embedding.tobytes()))
    conn.commit()
    conn.close()
    print(f'Added face for {name}')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python add_face.py <image_path> <name>')
    else:
        add_face(sys.argv[1], sys.argv[2])
