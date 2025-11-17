from app.models.employee import Employee, AttendanceRecord
from app.schemas.employee import EmployeeCreate, AttendanceRecordCreate, Employee as EmployeeSchema
from app.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func

def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def create_employee(db: Session, employee: EmployeeCreate):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def get_attendance(db: Session, employee_id: int):
    """
    Lấy danh sách điểm danh của nhân viên với thông tin ca làm việc từ bảng shifts
    """
    from app.models.shift import Shift
    from sqlalchemy import func, Date
    
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id
    ).all()
    
    # Convert records sang dict format
    result = []
    for record in records:
        # Lấy thông tin ca làm việc từ bảng shifts theo ngày điểm danh
        shift = None
        if record.timestamp_in:
            # Lấy ngày từ timestamp_in (chỉ phần date, không có time)
            attendance_date = record.timestamp_in.date()
            shift = db.query(Shift).filter(
                Shift.employee_id == employee_id,
                func.date(Shift.date) == attendance_date
            ).first()
        
        # Nếu có shift thì lấy thời gian từ shift, không thì dùng mặc định
        start_time = str(shift.start_time) if shift and shift.start_time else "08:00:00"
        end_time = str(shift.end_time) if shift and shift.end_time else "17:00:00"
        
        # Chuyển format từ HH:MM:SS sang HH:MM
        if len(start_time) > 5:
            start_time = start_time[:5]
        if len(end_time) > 5:
            end_time = end_time[:5]
        
        # Kiểm tra xem có phải tăng ca không
        # Thứ 7 (weekday=5) và Chủ nhật (weekday=6) tự động là tăng ca
        is_weekend_overtime = False
        if record.timestamp_in:
            day_of_week = record.timestamp_in.weekday()  # 0=Monday, 6=Sunday
            is_weekend_overtime = day_of_week in [5, 6]  # Thứ 7 và CN
        
        # Nếu là cuối tuần hoặc shift có đánh dấu overtime thì là tăng ca
        is_overtime = is_weekend_overtime or (bool(shift.is_overtime) if shift and hasattr(shift, 'is_overtime') and shift.is_overtime is not None else False)
        overtime_note = shift.overtime_note if shift and hasattr(shift, 'overtime_note') else None
        
        # Nếu là cuối tuần mà chưa có note thì thêm note mặc định
        if is_weekend_overtime and not overtime_note:
            overtime_note = "Tăng ca cuối tuần"
        
        record_dict = {
            "id": record.id,
            "employee_id": record.employee_id,
            "timestamp_in": record.timestamp_in.isoformat() if record.timestamp_in else None,
            "timestamp_out": None,  # Không có trong database
            "status": record.status,
            "photo_path": record.photo_path,
            "device_id": getattr(record, 'device_id', None),
            "start_time": start_time,
            "end_time": end_time,
            "is_overtime": is_overtime,
            "overtime_note": overtime_note
        }
        result.append(record_dict)
    
    return result

def create_attendance(db: Session, attendance: AttendanceRecordCreate):
    from datetime import datetime, date
    
    # Kiểm tra xem nhân viên đã điểm danh trong ngày hôm nay chưa
    today = date.today()
    existing_attendance = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == attendance.employee_id,
        func.date(AttendanceRecord.timestamp_in) == today
    ).first()
    
    if existing_attendance:
        # Đã điểm danh rồi, trả về bản ghi cũ
        return existing_attendance
    
    # Chưa điểm danh, tạo mới
    db_attendance = AttendanceRecord(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def lock_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.is_locked = 1
        db.commit()
        db.refresh(employee)
    return employee

def unlock_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.is_locked = 0
        db.commit()
        db.refresh(employee)
    return employee
