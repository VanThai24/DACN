"""
Monitor Realtime - Xem Records Mới Ngay Khi Được Tạo
Chạy script này và để nó chạy, mỗi khi có điểm danh mới sẽ hiện ngay
"""

import mysql.connector
import time
from datetime import datetime

print("=" * 80)
print("🔍 MONITOR REALTIME - THEO DÕI ĐIỂM DANH")
print("=" * 80)
print("Đang chạy... Mỗi khi có điểm danh mới sẽ hiện ở đây")
print("Press Ctrl+C to stop")
print("=" * 80)

last_id = 0

# Get current max ID
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)
cursor = db.cursor()
cursor.execute("SELECT MAX(id) FROM attendance_records")
result = cursor.fetchone()
last_id = result[0] if result[0] else 0
cursor.close()
db.close()

print(f"✅ Starting monitor from ID: {last_id}")
print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
print("-" * 80)

try:
    while True:
        # Check for new records
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="attendance_db"
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                a.id,
                e.name,
                a.timestamp_in,
                a.status
            FROM attendance_records a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.id > %s
            ORDER BY a.id ASC
        """, (last_id,))
        
        new_records = cursor.fetchall()
        
        if new_records:
            for record_id, name, timestamp, status in new_records:
                time_str = timestamp.strftime('%H:%M:%S')
                print(f"🎉 NEW RECORD!")
                print(f"   ID:   {record_id}")
                print(f"   Name: {name}")
                print(f"   Time: {time_str}")
                print(f"   Status: {status}")
                print("-" * 80)
                last_id = record_id
        
        cursor.close()
        db.close()
        
        time.sleep(1)  # Check every second
        
except KeyboardInterrupt:
    print("\n\n✅ Monitor stopped")
    print("=" * 80)
