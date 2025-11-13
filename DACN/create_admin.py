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

# Kiểm tra xem đã có admin chưa
cursor.execute("SELECT * FROM users WHERE Username = 'admin'")
existing_admin = cursor.fetchone()

if existing_admin:
    print(f"Tìm thấy tài khoản admin hiện tại:")
    print(f"ID: {existing_admin[0]}")
    print(f"Username: {existing_admin[1]}")
    print(f"PasswordHash: {existing_admin[2][:50]}...")
    print(f"Role: {existing_admin[3]}")
    print(f"EmployeeId: {existing_admin[4]}")
    print("\n")
    
    if existing_admin[3].lower() != 'admin':
        print(f"⚠️  CẢNH BÁO: Role hiện tại là '{existing_admin[3]}' (phải là 'Admin' với chữ A viết hoa)")
        print("   Cần cập nhật để có thể đăng nhập!")
    
    update = input("Bạn có muốn cập nhật lại mật khẩu và role không? (y/n): ")
    if update.lower() == 'y':
        new_password = input("Nhập mật khẩu mới (hoặc Enter để giữ nguyên mật khẩu cũ): ")
        
        if new_password:
            # Mã hóa mật khẩu bằng BCrypt
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, role = 'Admin' 
                WHERE Username = 'admin'
            """, (hashed,))
            print(f"✅ Đã cập nhật mật khẩu mới: {new_password}")
        else:
            # Chỉ cập nhật Role, giữ nguyên password
            cursor.execute("""
                UPDATE users 
                SET role = 'Admin' 
                WHERE Username = 'admin'
            """)
            print(f"✅ Đã cập nhật Role thành 'Admin' (giữ nguyên mật khẩu cũ)")
        
        conn.commit()
else:
    print("Không tìm thấy tài khoản admin. Tạo mới...")
    password = input("Nhập mật khẩu cho admin (hoặc Enter để dùng '123456'): ") or "123456"
    
    # Mã hóa mật khẩu bằng BCrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("""
        INSERT INTO users (Username, password_hash, role) 
        VALUES (%s, %s, 'Admin')
    """, ('admin', hashed))
    conn.commit()
    print(f"✅ Đã tạo tài khoản admin với mật khẩu: {password}")

# Hiển thị tất cả users
print("\n" + "="*60)
print("DANH SÁCH TẤT CẢ TÀI KHOẢN:")
print("="*60)
cursor.execute("SELECT Id, Username, role FROM users")
all_users = cursor.fetchall()
for user in all_users:
    print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")

cursor.close()
conn.close()

print("\n✅ Xong! Bây giờ bạn có thể đăng nhập bằng:")
print("   Username: admin")
print("   Password: [mật khẩu bạn vừa nhập]")
