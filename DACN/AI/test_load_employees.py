"""
Test load employees từ database giống code trong main.py
"""

import mysql.connector
import numpy as np

print("=" * 100)
print("TEST LOAD EMPLOYEES TỪ DATABASE (GIỐNG MAIN.PY)")
print("=" * 100)

try:
    # Lấy embeddings từ database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="attendance_db"
    )
    cursor = db.cursor()
    
    print("\n✅ Kết nối database thành công!")
    
    # 🔥 EMBEDDING MATCHING: Lấy tất cả nhân viên có embedding
    cursor.execute("""
        SELECT id, name, 
               COALESCE(face_encoding, face_embedding) as encoding
        FROM employees 
        WHERE face_encoding IS NOT NULL OR face_embedding IS NOT NULL
    """)
    employees_db = cursor.fetchall()
    cursor.close()
    db.close()
    
    print(f"✅ Query thành công: {len(employees_db)} rows")
    
    # Parse embeddings
    employee_data = []
    for emp_id, name, encoding_blob in employees_db:
        if encoding_blob:
            # Blob là bytes, convert về numpy array
            encoding = np.frombuffer(encoding_blob, dtype=np.float32)
            employee_data.append({
                'id': emp_id,
                'name': name,
                'embedding': encoding
            })
            print(f"  ✅ {emp_id}: {name} - Embedding {encoding.shape}")
    
    print(f"\n✅ Loaded {len(employee_data)} employees with embeddings")
    
    print("\n" + "=" * 100)
    print("DANH SÁCH NHÂN VIÊN:")
    print("=" * 100)
    for emp in employee_data:
        print(f"  ID: {emp['id']:<5} | Name: {emp['name']:<25} | Embedding: {emp['embedding'].shape}")
    
except Exception as e:
    print(f"❌ LỖI: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
