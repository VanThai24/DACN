"""
Xem chi tiết attendance records và shifts
"""

import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

print("=" * 120)
print("ĐIỂM DANH VÀ CA LÀM VIỆC HÔM NAY")
print("=" * 120)

today = datetime.now().date()

# Lấy tất cả attendance records hôm nay với thông tin ca
cursor.execute("""
    SELECT 
        a.id AS att_id,
        e.name,
        a.timestamp_in,
        a.status,
        a.shift_id,
        s.start_time,
        s.end_time
    FROM attendance_records a
    JOIN employees e ON a.employee_id = e.id
    LEFT JOIN shifts s ON a.shift_id = s.id
    WHERE DATE(a.timestamp_in) = %s
    ORDER BY a.timestamp_in DESC
""", (today,))

records = cursor.fetchall()

if records:
    print(f"\n{'ID':<5} | {'Tên':<20} | {'Thời gian check-in':<20} | {'Status':<10} | {'Shift ID':<10} | {'Ca làm việc':<15}")
    print("-" * 120)
    for r in records:
        shift_time = f"{r[5]}-{r[6]}" if r[5] and r[6] else "Chưa có ca"
        shift_id = r[4] if r[4] else "NULL"
        print(f"{r[0]:<5} | {r[1]:<20} | {r[2]} | {r[3]:<10} | {shift_id:<10} | {shift_time:<15}")
    
    print(f"\n📊 Tổng: {len(records)} lượt điểm danh")
else:
    print("\n⚠️ Chưa có điểm danh nào hôm nay!")

# Hiển thị tất cả ca hôm nay
print("\n" + "=" * 120)
print("TẤT CẢ CA LÀM VIỆC HÔM NAY")
print("=" * 120)

cursor.execute("""
    SELECT s.id, e.name, s.start_time, s.end_time
    FROM shifts s
    JOIN employees e ON s.employee_id = e.id
    WHERE DATE(s.date) = %s
    ORDER BY e.name, s.start_time
""", (today,))

shifts = cursor.fetchall()

if shifts:
    print(f"\n{'Shift ID':<10} | {'Nhân viên':<20} | {'Giờ bắt đầu':<12} | {'Giờ kết thúc':<12}")
    print("-" * 120)
    for s in shifts:
        print(f"{s[0]:<10} | {s[1]:<20} | {str(s[2]):<12} | {str(s[3]):<12}")
    
    print(f"\n📊 Tổng: {len(shifts)} ca")
else:
    print("\n⚠️ Chưa có ca nào được tạo!")

cursor.close()
db.close()

print("\n" + "=" * 120)
