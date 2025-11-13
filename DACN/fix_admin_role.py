import mysql.connector
import bcrypt

# Kết nối database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)

cursor = conn.cursor()

print("Đang cập nhật Role của admin từ 'admin' thành 'Admin'...\n")

# Cập nhật Role
cursor.execute("""
    UPDATE users 
    SET role = 'Admin' 
    WHERE Username = 'admin' AND role = 'admin'
""")

affected_rows = cursor.rowcount
conn.commit()

if affected_rows > 0:
    print(f"✅ Đã cập nhật Role thành công!")
else:
    print(f"ℹ️  Không có thay đổi (Role đã đúng là 'Admin')")

# Hiển thị tài khoản admin
cursor.execute("SELECT Id, Username, role, employee_id FROM users WHERE Username = 'admin'")
admin = cursor.fetchone()

print("\n" + "="*60)
print("THÔNG TIN TÀI KHOẢN ADMIN:")
print("="*60)
print(f"ID: {admin[0]}")
print(f"Username: {admin[1]}")
print(f"Role: {admin[2]}")
print(f"EmployeeId: {admin[3]}")

print("\n✅ Bây giờ bạn có thể đăng nhập vào AdminWeb bằng tài khoản admin!")

cursor.close()
conn.close()
