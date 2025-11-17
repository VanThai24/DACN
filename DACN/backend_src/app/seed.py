from app.database import SessionLocal
from app.models.employee import Employee, AttendanceRecord
from app.models.user import User
from app.models.device import Device
from app.models.shift import Shift
from app.models.report import Report
from datetime import datetime, time

def seed():
    db = SessionLocal()
    # Thêm nhân viên mẫu
    emp1 = Employee(name="Nguyễn Văn A", department="Kỹ thuật", role="Nhân viên")
    emp2 = Employee(name="Trần Thị B", department="Nhân sự", role="Quản lý")
    db.add_all([emp1, emp2])
    db.commit()
    # Thêm user mẫu
    user1 = User(username="admin", password_hash="admin123", role="admin", employee_id=None)
    user2 = User(username="nva", password_hash="123456", role="employee", employee_id=emp1.id)
    db.add_all([user1, user2])
    db.commit()
    # Thêm thiết bị mẫu
    device1 = Device(name="Kiosk 1", location="Sảnh chính", api_key="kiosk1key")
    db.add(device1)
    db.commit()
    # Thêm ca làm mẫu
    shift1 = Shift(employee_id=emp1.id, date=datetime(2025,10,15), start_time=time(8,0), end_time=time(17,0))
    db.add(shift1)
    db.commit()
    # Thêm báo cáo mẫu
    report1 = Report(created_at=datetime.now(), type="daily", file_path="/reports/daily_20251015.xlsx", created_by=user1.id)
    db.add(report1)
    db.commit()
    # Thêm điểm danh mẫu
    att1 = AttendanceRecord(employee_id=emp1.id, device_id=device1.id, timestamp_in=datetime(2025,10,15,8,5), status="in", photo_path="/photos/in1.jpg")
    db.add(att1)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
