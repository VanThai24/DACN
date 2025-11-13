"""
Script chuẩn hóa Role trong database
- Admin (cho AdminWeb)
- Employee (cho Mobile App)
"""
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="12345",
    database="attendance_db"
)

cursor = conn.cursor()

print("\n🔧 CHUẨN HÓA ROLE TRONG DATABASE")
print("="*60)

# Chuẩn hóa tất cả role
updates = [
    ("UPDATE users SET role = 'Admin' WHERE role LIKE 'admin'", "Admin"),
    ("UPDATE users SET role = 'Employee' WHERE role LIKE 'employee'", "Employee"),
    ("UPDATE users SET role = 'Manager' WHERE role LIKE 'manager'", "Manager"),
]

for sql, role_name in updates:
    cursor.execute(sql)
    if cursor.rowcount > 0:
        print(f"✅ Đã cập nhật {cursor.rowcount} tài khoản thành Role='{role_name}'")

conn.commit()

# Hiển thị lại danh sách
print("\n📋 DANH SÁCH SAU KHI CHUẨN HÓA:")
print("="*60)

cursor.execute("""
    SELECT u.id, u.username, u.role, e.name as employee_name
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    ORDER BY u.id
""")

for row in cursor.fetchall():
    print(f"ID {row[0]:3d} | {row[1]:15s} | Role: {row[2]:10s} | {row[3] or 'N/A'}")

print("="*60)
print("\n✅ Hoàn tất chuẩn hóa!")
print("\n📱 HƯỚNG DẪN ĐĂNG NHẬP:")
print("   AdminWeb: Dùng tài khoản có Role='Admin'")
print("   Mobile App: Dùng tài khoản có Role='Employee'")
print("="*60)

cursor.close()
conn.close()
