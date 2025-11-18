import mysql.connector
from datetime import datetime

# Kết nối database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="attendance_db"
)

cursor = db.cursor()

# Kiểm tra shifts với attendance_records
query = """
SELECT 
    s.id as shift_id,
    s.employee_id,
    e.name,
    DATE(s.date) as date,
    s.start_time,
    s.end_time,
    s.is_overtime,
    a.id as attendance_id,
    a.timestamp_in
FROM shifts s
JOIN employees e ON s.employee_id = e.id
LEFT JOIN attendance_records a ON a.employee_id = s.employee_id 
    AND DATE(a.timestamp_in) = DATE(s.date)
WHERE DATE(s.date) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY s.date DESC, s.start_time DESC
LIMIT 20
"""

cursor.execute(query)
results = cursor.fetchall()

print("\n" + "="*100)
print("SHIFTS vs ATTENDANCE DATA (Last 7 days)")
print("="*100)
print(f"{'Shift ID':<10} {'Emp ID':<8} {'Name':<20} {'Date':<12} {'Start':<8} {'End':<8} {'OT':<4} {'Att ID':<8} {'Timestamp In'}")
print("-"*100)

for row in results:
    shift_id, emp_id, name, date, start_time, end_time, is_overtime, att_id, timestamp_in = row
    
    # Format date
    date_str = date.strftime('%d/%m/%Y') if date else '-'
    
    # Format times
    start_str = str(start_time) if start_time else '-'
    end_str = str(end_time) if end_time else '-'
    
    # Format timestamp_in
    time_in_str = timestamp_in.strftime('%H:%M:%S') if timestamp_in else '-'
    
    # OT flag
    ot_str = 'Yes' if is_overtime else 'No'
    
    # Attendance ID
    att_id_str = str(att_id) if att_id else '-'
    
    print(f"{shift_id:<10} {emp_id:<8} {name:<20} {date_str:<12} {start_str:<8} {end_str:<8} {ot_str:<4} {att_id_str:<8} {time_in_str}")

print("-"*100)
print(f"Total: {len(results)} records")
print("="*100)

# Kiểm tra attendance_records không có shift
query2 = """
SELECT 
    a.id,
    a.employee_id,
    e.name,
    DATE(a.timestamp_in) as date,
    TIME(a.timestamp_in) as time_in,
    a.shift_id
FROM attendance_records a
JOIN employees e ON a.employee_id = e.id
WHERE DATE(a.timestamp_in) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY a.timestamp_in DESC
LIMIT 10
"""

cursor.execute(query2)
results2 = cursor.fetchall()

print("\n" + "="*100)
print("ATTENDANCE RECORDS (Last 7 days)")
print("="*100)
print(f"{'Att ID':<10} {'Emp ID':<8} {'Name':<20} {'Date':<12} {'Time In':<10} {'Shift ID'}")
print("-"*100)

for row in results2:
    att_id, emp_id, name, date, time_in, shift_id = row
    date_str = date.strftime('%d/%m/%Y') if date else '-'
    time_str = str(time_in) if time_in else '-'
    shift_str = str(shift_id) if shift_id else 'NULL'
    print(f"{att_id:<10} {emp_id:<8} {name:<20} {date_str:<12} {time_str:<10} {shift_str}")

print("-"*100)
print(f"Total: {len(results2)} attendance records")
print("="*100)

cursor.close()
db.close()
