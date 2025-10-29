import bcrypt
import pymysql

# Kết nối MySQL
conn = pymysql.connect(host='localhost', user='root', password='12345', database='attendance_db')
cur = conn.cursor()

# Tạo hash bcrypt cho mật khẩu mới (ví dụ: admin123)
new_password = 'admin123'
hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

# Cập nhật mật khẩu admin
cur.execute("UPDATE users SET password_hash=%s WHERE username='admin'", (hashed,))
conn.commit()
cur.close()
conn.close()
print("Đã cập nhật mật khẩu admin sang bcrypt!")
