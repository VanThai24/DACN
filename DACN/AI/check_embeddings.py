"""
Kiểm tra employees có embedding trong database
"""

import mysql.connector
import numpy as np

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

cursor.execute("""
    SELECT id, name, 
           face_encoding,
           face_embedding,
           COALESCE(face_encoding, face_embedding) as enc
    FROM employees
""")

rows = cursor.fetchall()

print("=" * 100)
print("KIỂM TRA EMPLOYEES VÀ EMBEDDINGS")
print("=" * 100)

print(f"\n📊 Tổng số nhân viên: {len(rows)}")
print(f"✅ Có embedding: {sum(1 for r in rows if r[4])}")
print(f"❌ Không có embedding: {sum(1 for r in rows if not r[4])}")

print("\n" + "=" * 100)
print("CHI TIẾT:")
print("=" * 100)

for r in rows:
    emp_id, name, face_enc, face_emb, combined = r
    
    status = ""
    if face_enc:
        enc_len = len(np.frombuffer(face_enc, dtype=np.float32))
        status = f"face_encoding ({enc_len}d)"
    elif face_emb:
        emb_len = len(np.frombuffer(face_emb, dtype=np.float32))
        status = f"face_embedding ({emb_len}d)"
    else:
        status = "❌ KHÔNG CÓ"
    
    print(f"{emp_id:<5} | {name:<25} | {status}")

cursor.close()
db.close()

print("\n" + "=" * 100)
