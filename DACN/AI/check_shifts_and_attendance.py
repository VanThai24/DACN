"""
Script: Kiểm tra ca làm việc và attendance với shift_id
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

print("=" * 100)
print("CA LÀM VIỆC HÔM NAY:")
print("=" * 100)

today = datetime.now().date()
cursor.execute("""
    SELECT s.id, e.name, s.date, s.start_time, s.end_time
    FROM shifts s
    JOIN employees e ON s.employee_id = e.id
    WHERE DATE(s.date) = %s
    ORDER BY e.name, s.start_time
""", (today,))

shifts = cursor.fetchall()
print(f"{'Shift ID':<10} | {'Tên NV':<20} | {'Ngày':<12} | {'Giờ vào':<10} | {'Giờ ra':<10}")
print("-" * 100)
for shift in shifts:
    print(f"{shift[0]:<10} | {shift[1]:<20} | {shift[2]} | {shift[3]} | {shift[4]}")

print(f"\n📊 Tổng: {len(shifts)} ca làm việc")

print("\n" + "=" * 100)
print("ĐIỂM DANH HÔM NAY (Có shift_id):")
print("=" * 100)

cursor.execute("""
    SELECT 
        a.id, 
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
    print(f"{'ID':<5} | {'Tên':<20} | {'Thời gian':<20} | {'Status':<10} | {'Shift ID':<10} | {'Ca làm việc':<20}")
    print("-" * 100)
    for rec in records:
        shift_time = f"{rec[5]}-{rec[6]}" if rec[5] and rec[6] else "Ngoài giờ"
        shift_id = rec[4] if rec[4] else "NULL"
        print(f"{rec[0]:<5} | {rec[1]:<20} | {rec[2]} | {rec[3]:<10} | {shift_id:<10} | {shift_time:<20}")
    
    # Đếm có shift và không có shift
    with_shift = sum(1 for r in records if r[4])
    without_shift = len(records) - with_shift
    
    print(f"\n📊 Tổng: {len(records)} records")
    print(f"   ✅ Có ca: {with_shift}")
    print(f"   ⚠️ Không có ca: {without_shift}")
else:
    print("Chưa có điểm danh nào hôm nay!")

cursor.close()
db.close()

print("\n" + "=" * 100)
print("✅ HOÀN TẤT!")
print("=" * 100)
