from backend_src.app.models.employee import Employee, AttendanceRecord
from backend_src.app.schemas.employee import EmployeeCreate, AttendanceRecordCreate, Employee as EmployeeSchema
from backend_src.app.database import SessionLocal
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
    return db.query(AttendanceRecord).filter(AttendanceRecord.employee_id == employee_id).all()

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
