"""
Test xem AI có đọc đúng dữ liệu từ database không
"""
import sqlite3
import numpy as np
from pathlib import Path

# Đường dẫn database giống trong db.py
DB_PATH = Path(__file__).parent.parent / "backend_src" / "dacn.db"

print(f"📂 Đang kiểm tra database: {DB_PATH}")
print(f"📍 File tồn tại: {DB_PATH.exists()}")

if not DB_PATH.exists():
    print("❌ Database không tồn tại!")
    exit(1)

# Kết nối database
conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

# Kiểm tra table employees
print("\n📊 Kiểm tra table employees:")
c.execute("SELECT COUNT(*) FROM employees")
total = c.fetchone()[0]
print(f"   Tổng số employees: {total}")

# Kiểm tra employees có face_embedding
c.execute("SELECT COUNT(*) FROM employees WHERE face_embedding IS NOT NULL")
with_face = c.fetchone()[0]
print(f"   Employees có face_embedding: {with_face}")

# Lấy danh sách chi tiết
print("\n👥 Danh sách employees có face:")
c.execute("SELECT id, name, LENGTH(face_embedding) FROM employees WHERE face_embedding IS NOT NULL")
rows = c.fetchall()

if not rows:
    print("   ❌ KHÔNG CÓ DỮ LIỆU!")
else:
    for row in rows:
        emp_id, name, embedding_size = row
        print(f"   ✅ ID: {emp_id}, Name: {name}, Embedding: {embedding_size} bytes")

# Test đọc embedding như trong app.py
print("\n🔬 Test đọc embeddings (giống app.py):")
c.execute('SELECT name, face_embedding FROM employees WHERE face_embedding IS NOT NULL')
data = c.fetchall()

embeddings = []
for name, embedding_blob in data:
    if embedding_blob:
        try:
            # Thử float64
            embedding = np.frombuffer(embedding_blob, dtype=np.float64)
            if len(embedding) == 0:
                embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            embeddings.append((name, embedding))
            print(f"   ✅ {name}: Embedding shape {embedding.shape}, dtype {embedding.dtype}")
        except Exception as e:
            print(f"   ❌ {name}: Lỗi decode - {e}")

print(f"\n✨ Tổng số embeddings đọc được: {len(embeddings)}")

conn.close()

if len(embeddings) > 0:
    print("\n🎉 AI ĐANG ĐỌC ĐÚNG DỮ LIỆU TỪ DATABASE!")
else:
    print("\n❌ AI KHÔNG ĐỌC ĐƯỢC DỮ LIỆU!")
