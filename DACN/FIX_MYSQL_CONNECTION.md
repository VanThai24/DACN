# FIX MYSQL CONNECTION ERROR

## VẤN ĐỀ:
```
Host 'LAPTOP-OVMVKSDU' is not allowed to connect to this MySQL server
```

## NGUYÊN NHÂN:
MySQL không cho phép user 'root' connect từ hostname 'LAPTOP-OVMVKSDU'

## GIẢI PHÁP:

### Bước 1: Mở MySQL Command Line hoặc MySQL Workbench

```powershell
# Trong PowerShell
mysql -u root -p
# Nhập password: 12345
```

### Bước 2: Chạy các lệnh SQL sau:

```sql
-- Xem user hiện tại
SELECT User, Host FROM mysql.user WHERE User='root';

-- Tạo user root cho tất cả hosts (nếu chưa có)
CREATE USER 'root'@'%' IDENTIFIED BY '12345';

-- Hoặc nếu đã tồn tại, update password:
ALTER USER 'root'@'%' IDENTIFIED BY '12345';

-- Grant full permissions
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- Hoặc chỉ grant cho database cụ thể (an toàn hơn):
GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SELECT User, Host FROM mysql.user WHERE User='root';
```

### Bước 3: Restart MySQL service (nếu cần)

```powershell
# Trong PowerShell với quyền Admin
Restart-Service MySQL80  # Hoặc tên service MySQL của bạn

# Hoặc
net stop MySQL80
net start MySQL80
```

### Bước 4: Test lại connection

```powershell
# Restart AdminWeb
cd D:\DACN\DACN
dotnet run
```

---

## ALTERNATIVE: Nếu không muốn mở % host

Thay vì cho phép tất cả hosts (`%`), chỉ cho phép localhost và hostname:

```sql
-- Tạo user cho localhost
GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'localhost' IDENTIFIED BY '12345';

-- Tạo user cho hostname cụ thể
GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'LAPTOP-OVMVKSDU' IDENTIFIED BY '12345';

-- Tạo user cho 127.0.0.1
GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'127.0.0.1' IDENTIFIED BY '12345';

FLUSH PRIVILEGES;
```

---

## QUICK FIX (ONE-LINER):

```sql
mysql -u root -p -e "GRANT ALL PRIVILEGES ON attendance_db.* TO 'root'@'%' IDENTIFIED BY '12345'; FLUSH PRIVILEGES;"
```

---

## SAU KHI FIX:

1. ✅ Route `/Users` đã hoạt động
2. ✅ Redirect đến Login đúng
3. ✅ Sau khi fix MySQL, đăng nhập sẽ thành công
4. ✅ Truy cập `/Users/Index` sẽ hiển thị danh sách users

## TẤT CẢ ĐÃ ĐƯỢC FIX:
- ✅ DateTime.Value error → Fixed
- ✅ Role database → Fixed (Admin với chữ A viết hoa)
- ✅ UsersController routing → Fixed (explicit routes)
- ❌ MySQL connection → CẦN FIX BẰNG SQL COMMANDS Ở TRÊN

Chỉ còn 1 bước cuối cùng là fix MySQL permissions!
