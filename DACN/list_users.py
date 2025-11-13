"""
Kiểm tra và hiển thị tất cả users trong database
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

print("\n" + "="*80)
print("📋 DANH SÁCH TÀI KHOẢN TRONG DATABASE")
print("="*80)

cursor.execute("""
    SELECT u.id, u.username, u.role, u.employee_id, e.name as employee_name
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    ORDER BY u.id
""")

users = cursor.fetchall()

for user in users:
    print(f"\n👤 ID: {user[0]}")
    print(f"   Username: {user[1]}")
    print(f"   Role: {user[2]}")
    print(f"   Employee ID: {user[3] if user[3] else 'NULL'}")
    print(f"   Employee Name: {user[4] if user[4] else 'N/A'}")
    print("-" * 80)

print(f"\n📊 Tổng số tài khoản: {len(users)}")
print("="*80)

# Kiểm tra xem có tài khoản Admin không
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
admin_count = cursor.fetchone()[0]

if admin_count == 0:
    print("\n⚠️  CẢNH BÁO: Không có tài khoản Admin!")
    print("   Bạn cần tạo tài khoản Admin để đăng nhập AdminWeb.")
else:
    print(f"\n✅ Có {admin_count} tài khoản Admin")

# Kiểm tra xem có tài khoản Employee không
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Employee'")
employee_count = cursor.fetchone()[0]

if employee_count == 0:
    print("⚠️  CẢNH BÁO: Không có tài khoản Employee!")
    print("   Bạn cần tạo tài khoản Employee để đăng nhập Mobile App.")
else:
    print(f"✅ Có {employee_count} tài khoản Employee (có thể đăng nhập Mobile App)")

cursor.close()
conn.close()
