"""
Script đơn giản để thêm tài khoản test nhân viên vào MySQL
"""
import mysql.connector
import bcrypt

# Kết nối MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="12345",
    database="attendance_db"
)

cursor = conn.cursor()

try:
    # Kiểm tra tài khoản đã tồn tại
    cursor.execute("SELECT * FROM users WHERE Username = 'testuser'")
    existing = cursor.fetchone()
    
    if existing:
        print("❌ Tài khoản 'testuser' đã tồn tại!")
        print(f"   Username: testuser")
        
        # Cập nhật mật khẩu
        choice = input("\nBạn có muốn reset mật khẩu thành '123456'? (y/n): ")
        if choice.lower() == 'y':
            hashed = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET PasswordHash = %s WHERE Username = 'testuser'",
                (hashed.decode('utf-8'),)
            )
            conn.commit()
            print("✅ Đã reset mật khẩu thành công!")
    else:
        # Tạo nhân viên mới
        print("\n📝 Tạo nhân viên test...")
        cursor.execute("""
            INSERT INTO employees (name, department, role, phone, email, is_locked)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ("Nguyễn Văn Test", "Phòng IT", "Nhân viên", "0123456789", "testuser@company.com", 0))
        
        employee_id = cursor.lastrowid
        print(f"✅ Đã tạo nhân viên: Nguyễn Văn Test (ID: {employee_id})")
        
        # Hash mật khẩu
        password = "123456"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Tạo user - CHỈ role='Employee' mới đăng nhập mobile được
        print("\n🔐 Tạo tài khoản đăng nhập...")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, employee_id)
            VALUES (%s, %s, %s, %s)
        """, ("testuser", hashed_password.decode('utf-8'), "Employee", employee_id))
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ TẠO TÀI KHOẢN TEST THÀNH CÔNG!")
        print("="*60)
        print(f"👤 Tên nhân viên: Nguyễn Văn Test")
        print(f"🏢 Phòng ban: Phòng IT")
        print(f"💼 Chức vụ: Nhân viên")
        print(f"📞 SĐT: 0123456789")
        print(f"📧 Email: testuser@company.com")
        print("\n🔑 THÔNG TIN ĐĂNG NHẬP MOBILE APP:")
        print(f"   Username: testuser")
        print(f"   Password: 123456")
        print(f"   Role: Employee")
        print("="*60)
        print("\n⚠️  LƯU Ý: Chỉ tài khoản có Role='Employee' mới đăng nhập mobile app!")
        print("   Tài khoản Admin/Manager KHÔNG thể đăng nhập mobile app.\n")

except Exception as e:
    conn.rollback()
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
