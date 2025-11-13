"""
Script kiểm tra cấu trúc bảng trong MySQL
"""
import mysql.connector

# Kết nối MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="12345",
    database="attendance_db"
)

cursor = conn.cursor()

print("\n📋 Cấu trúc bảng EMPLOYEES:")
print("="*60)
cursor.execute("DESCRIBE employees")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]:<20} Null:{row[2]}")

print("\n📋 Cấu trúc bảng USERS:")
print("="*60)
cursor.execute("DESCRIBE users")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]:<20} Null:{row[2]}")

print("\n📊 Số lượng dữ liệu:")
print("="*60)
cursor.execute("SELECT COUNT(*) FROM employees")
emp_count = cursor.fetchone()[0]
print(f"  Employees: {emp_count}")

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"  Users: {user_count}")

cursor.close()
conn.close()
