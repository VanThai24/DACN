"""
Script: Tạo ca làm việc cho TẤT CẢ nhân viên
"""

import mysql.connector
from datetime import datetime, time, timedelta

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

print("=" * 100)
print("TẠO CA LÀM VIỆC CHO TẤT CẢ NHÂN VIÊN")
print("=" * 100)

# Lấy danh sách nhân viên
cursor.execute("SELECT id, name FROM employees ORDER BY id")
employees = cursor.fetchall()

print(f"\n📋 Danh sách nhân viên: {len(employees)} người")
for emp_id, emp_name in employees:
    print(f"   - {emp_id}: {emp_name}")

# Xóa các ca cũ để tạo mới
cursor.execute("DELETE FROM shifts")
db.commit()
print(f"\n🗑️ Đã xóa các ca cũ")

# Tạo ca cho 7 ngày (hôm nay + 6 ngày tới)
today = datetime.now().date()
total_created = 0

print(f"\n➕ Tạo ca làm việc (7 ngày)...")

for day_offset in range(7):
    work_date = today + timedelta(days=day_offset)
    
    for emp_id, emp_name in employees:
        # Ca sáng: 7:00 - 12:00
        cursor.execute("""
            INSERT INTO shifts (employee_id, date, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (emp_id, work_date, time(7, 0), time(12, 0)))
        
        # Ca chiều: 13:00 - 18:00
        cursor.execute("""
            INSERT INTO shifts (employee_id, date, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (emp_id, work_date, time(13, 0), time(18, 0)))
        
        total_created += 2
    
    db.commit()
    print(f"   ✅ Ngày {work_date}: Tạo {len(employees) * 2} ca")

print(f"\n✅ Tổng cộng: {total_created} ca làm việc")

# Hiển thị ca hôm nay
print("\n" + "=" * 100)
print("CA LÀM VIỆC HÔM NAY:")
print("=" * 100)

cursor.execute("""
    SELECT s.id, e.name, s.start_time, s.end_time
    FROM shifts s
    JOIN employees e ON s.employee_id = e.id
    WHERE DATE(s.date) = %s
    ORDER BY e.name, s.start_time
""", (today,))

shifts_today = cursor.fetchall()
print(f"{'Shift ID':<10} | {'Tên NV':<25} | {'Giờ vào':<10} | {'Giờ ra':<10}")
print("-" * 100)
for shift in shifts_today:
    print(f"{shift[0]:<10} | {shift[1]:<25} | {shift[2]} | {shift[3]}")

print(f"\n📊 Tổng ca hôm nay: {len(shifts_today)}")

cursor.close()
db.close()

print("\n" + "=" * 100)
print("✅ HOÀN TẤT! Giờ test lại desktop app!")
print("=" * 100)
