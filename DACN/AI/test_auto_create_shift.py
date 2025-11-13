"""
Test logic tự động tạo ca làm việc khi điểm danh
"""

import mysql.connector
from datetime import datetime, time

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

print("=" * 100)
print("TEST TỰ ĐỘNG TẠO CA KHI ĐIỂM DANH")
print("=" * 100)

# Giả lập điểm danh của nhân viên ID 81 (Đặng Văn Thái)
employee_id = 81
employee_name = "Đặng Văn Thái"
now = datetime.now()
current_time = now.time()
current_date = now.date()

print(f"\n🕐 Giờ hiện tại: {current_time}")
print(f"👤 Nhân viên: {employee_name} (ID: {employee_id})")

# Logic xác định ca dựa vào giờ điểm danh
if time(6, 0) <= current_time < time(12, 30):
    shift_start = time(7, 0)
    shift_end = time(12, 0)
    shift_name = "Ca sáng"
else:
    shift_start = time(13, 0)
    shift_end = time(18, 0)
    shift_name = "Ca chiều"

print(f"📋 Ca được xác định: {shift_name} ({shift_start}-{shift_end})")

# Kiểm tra ca đã tồn tại chưa
cursor.execute("""
    SELECT id FROM shifts 
    WHERE employee_id = %s 
    AND DATE(date) = %s
    AND start_time = %s
    AND end_time = %s
    LIMIT 1
""", (employee_id, current_date, shift_start, shift_end))
existing_shift = cursor.fetchone()

if existing_shift:
    shift_id = existing_shift[0]
    print(f"✅ Ca đã tồn tại: Shift ID {shift_id}")
else:
    # Tạo ca mới (DRY RUN - không commit)
    print(f"➕ Ca chưa tồn tại, sẽ tạo mới...")
    cursor.execute("""
        INSERT INTO shifts (employee_id, date, start_time, end_time)
        VALUES (%s, %s, %s, %s)
    """, (employee_id, current_date, shift_start, shift_end))
    shift_id = cursor.lastrowid
    db.commit()  # Commit để test thật
    print(f"✅ Đã tạo ca mới: Shift ID {shift_id}")

# Hiển thị thông tin ca
shift_info = f"{shift_name}: {shift_start.strftime('%H:%M')}-{shift_end.strftime('%H:%M')}"
print(f"\n📊 Kết quả: {shift_info}")

# Xem tất cả ca của nhân viên này hôm nay
print(f"\n" + "=" * 100)
print(f"TẤT CẢ CA CỦA {employee_name} HÔM NAY:")
print("=" * 100)

cursor.execute("""
    SELECT id, start_time, end_time
    FROM shifts
    WHERE employee_id = %s
    AND DATE(date) = %s
    ORDER BY start_time
""", (employee_id, current_date))

shifts = cursor.fetchall()
if shifts:
    for s in shifts:
        print(f"  Shift ID {s[0]}: {s[1]} - {s[2]}")
else:
    print("  Không có ca nào!")

cursor.close()
db.close()

print("\n" + "=" * 100)
print("✅ TEST HOÀN TẤT!")
print("=" * 100)
