"""
Script: Thêm cột shift_id vào bảng attendance_records
Để lưu thông tin ca làm việc khi điểm danh
"""

import mysql.connector
from datetime import datetime, time

# Kết nối database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

print("=" * 80)
print("THÊM CỘT SHIFT_ID VÀO BẢNG ATTENDANCE_RECORDS")
print("=" * 80)

# 1. Kiểm tra xem cột shift_id đã tồn tại chưa
cursor.execute("DESCRIBE attendance_records")
columns = [row[0] for row in cursor.fetchall()]

if 'shift_id' in columns:
    print("✅ Cột shift_id đã tồn tại!")
else:
    print("➕ Thêm cột shift_id...")
    cursor.execute("""
        ALTER TABLE attendance_records 
        ADD COLUMN shift_id INT NULL AFTER device_id,
        ADD FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL
    """)
    db.commit()
    print("✅ Đã thêm cột shift_id thành công!")

# 2. Tạo một số ca làm việc mẫu nếu bảng shifts rỗng
cursor.execute("SELECT COUNT(*) FROM shifts")
shift_count = cursor.fetchone()[0]

if shift_count == 0:
    print("\n➕ Tạo ca làm việc mẫu...")
    
    # Lấy danh sách nhân viên
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    
    if len(employees) > 0:
        # Tạo ca sáng (7h-12h) và ca chiều (13h-18h) cho tất cả nhân viên hôm nay
        today = datetime.now().date()
        
        for emp_id, emp_name in employees:
            # Ca sáng
            cursor.execute("""
                INSERT INTO shifts (employee_id, date, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (emp_id, today, time(7, 0), time(12, 0)))
            
            # Ca chiều
            cursor.execute("""
                INSERT INTO shifts (employee_id, date, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (emp_id, today, time(13, 0), time(18, 0)))
            
            print(f"   ✅ Tạo ca cho: {emp_name}")
        
        db.commit()
        print(f"\n✅ Đã tạo {len(employees) * 2} ca làm việc!")
    else:
        print("⚠️ Không có nhân viên nào trong database!")

# 3. Hiển thị cấu trúc mới
print("\n" + "=" * 80)
print("CẤU TRÚC MỚI CỦA BẢNG ATTENDANCE_RECORDS:")
print("=" * 80)
cursor.execute("DESCRIBE attendance_records")
for row in cursor.fetchall():
    print(f"{row[0]:<20} | {row[1]:<15} | NULL: {row[2]}")

# 4. Hiển thị các ca làm việc
print("\n" + "=" * 80)
print("CÁC CA LÀM VIỆC:")
print("=" * 80)
cursor.execute("""
    SELECT s.id, e.name, s.date, s.start_time, s.end_time 
    FROM shifts s 
    JOIN employees e ON s.employee_id = e.id 
    ORDER BY s.date DESC, s.start_time
    LIMIT 10
""")
shifts = cursor.fetchall()

if shifts:
    print(f"{'ID':<5} | {'Tên':<20} | {'Ngày':<12} | {'Giờ vào':<10} | {'Giờ ra':<10}")
    print("-" * 80)
    for shift in shifts:
        print(f"{shift[0]:<5} | {shift[1]:<20} | {shift[2]} | {shift[3]} | {shift[4]}")
else:
    print("Không có ca làm việc nào!")

cursor.close()
db.close()

print("\n" + "=" * 80)
print("✅ HOÀN TẤT!")
print("=" * 80)
print("\nBước tiếp theo:")
print("1. Chạy update_desktop_with_shift.py để cập nhật code điểm danh")
print("2. Mở desktop app và test điểm danh lại")
