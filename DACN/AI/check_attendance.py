"""
Kiểm Tra Kết Quả Điểm Danh
Hiển thị các record attendance mới nhất
"""

import mysql.connector
from datetime import datetime, timedelta

print("=" * 80)
print("KIỂM TRA KỂT QUẢ ĐIỂM DANH")
print("=" * 80)

# Connect to database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()

# Get records from today
today = datetime.now().date()
print(f"\n📅 Ngày: {today.strftime('%d/%m/%Y')}")

cursor.execute("""
    SELECT 
        a.id,
        e.name,
        a.timestamp_in,
        a.status,
        a.device_id
    FROM attendance_records a
    JOIN employees e ON a.employee_id = e.id
    WHERE DATE(a.timestamp_in) = %s
    ORDER BY a.timestamp_in DESC
    LIMIT 20
""", (today,))

records = cursor.fetchall()

if len(records) == 0:
    print("\n⚠️  Không có record nào hôm nay")
else:
    print(f"\n✅ Tìm thấy {len(records)} records hôm nay:")
    print("\n" + "-" * 80)
    print(f"{'ID':<6} {'Tên':<30} {'Thời gian':<20} {'Status':<10} {'Device'}")
    print("-" * 80)
    
    for record_id, name, timestamp, status, device_id in records:
        time_str = timestamp.strftime('%H:%M:%S')
        print(f"{record_id:<6} {name:<30} {time_str:<20} {status:<10} {device_id}")

# Get statistics
cursor.execute("""
    SELECT 
        e.name,
        COUNT(*) as count
    FROM attendance_records a
    JOIN employees e ON a.employee_id = e.id
    WHERE DATE(a.timestamp_in) = %s
    GROUP BY e.name
    ORDER BY count DESC
""", (today,))

stats = cursor.fetchall()

if len(stats) > 0:
    print("\n" + "=" * 80)
    print("📊 THỐNG KÊ ĐIỂM DANH HÔM NAY")
    print("=" * 80)
    for name, count in stats:
        print(f"  {name:<30} : {count} lần")

# Get last 5 records (any date)
print("\n" + "=" * 80)
print("🕐 5 RECORDS MỚI NHẤT (Tất cả ngày)")
print("=" * 80)

cursor.execute("""
    SELECT 
        a.id,
        e.name,
        a.timestamp_in,
        a.status
    FROM attendance_records a
    JOIN employees e ON a.employee_id = e.id
    ORDER BY a.timestamp_in DESC
    LIMIT 5
""")

recent = cursor.fetchall()
for record_id, name, timestamp, status in recent:
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    print(f"  [{record_id}] {name:<25} - {time_str} - {status}")

cursor.close()
db.close()

print("\n" + "=" * 80)
print("✅ KIỂM TRA HOÀN TẤT")
print("=" * 80)
