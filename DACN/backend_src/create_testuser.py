"""
Script tạo user testuser vào database
"""
import mysql.connector
from passlib.hash import bcrypt

# Kết nối database
conn = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='12345',
    database='attendance_db'
)

cursor = conn.cursor()

# Kiểm tra user đã tồn tại chưa
cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
existing = cursor.fetchone()

if existing:
    print("❌ User 'testuser' đã tồn tại!")
    print(f"   ID: {existing[0]}")
else:
    # Hash password
    password = 'testuser123'
    hashed = bcrypt.hash(password)
    
    # Insert user mới
    cursor.execute(
        "INSERT INTO users (username, password, Role) VALUES (%s, %s, %s)",
        ('testuser', hashed, 'Admin')
    )
    conn.commit()
    
    print("✅ Tạo user thành công!")
    print(f"   Username: testuser")
    print(f"   Password: {password}")
    print(f"   Role: Admin")

# Hiển thị tất cả users
print("\n" + "="*50)
print("DANH SÁCH USERS:")
print("="*50)
cursor.execute("SELECT id, username, Role FROM users")
users = cursor.fetchall()

for user in users:
    print(f"ID: {user[0]:3} | Username: {user[1]:20} | Role: {user[2]}")

cursor.close()
conn.close()
