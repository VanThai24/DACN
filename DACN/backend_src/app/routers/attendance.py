
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import SessionLocal
from app.schemas.employee import AttendanceRecord, AttendanceRecordCreate
from app.crud.employee import get_attendance, create_attendance
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_attendance_api(attendance: AttendanceRecordCreate, db: Session = Depends(get_db)):
    """
    Ghi nhận một lượt điểm danh mới cho nhân viên.
    Kiểm tra nếu đã điểm danh trong ngày sẽ trả về thông báo.
    """
    from datetime import date
    from app.models.employee import AttendanceRecord as AttendanceRecordModel
    
    # Kiểm tra đã điểm danh trong ngày chưa
    today = date.today()
    existing = db.query(AttendanceRecordModel).filter(
        AttendanceRecordModel.employee_id == attendance.employee_id,
        func.date(AttendanceRecordModel.timestamp_in) == today
    ).first()
    
    if existing:
        # Đã điểm danh rồi
        return {
            "success": False,
            "message": "Bạn đã điểm danh hôm nay rồi",
            "already_checked_in": True,
            "timestamp": existing.timestamp_in.isoformat(),
            "attendance_id": existing.id
        }
    
    # Chưa điểm danh, tạo mới
    new_attendance = create_attendance(db, attendance)
    return {
        "success": True,
        "message": "Điểm danh thành công",
        "already_checked_in": False,
        "timestamp": new_attendance.timestamp_in.isoformat(),
        "attendance_id": new_attendance.id
    }

@router.get("/employee/{employee_id}")
def read_attendance(employee_id: int, db: Session = Depends(get_db)):
    """
    Lấy danh sách lịch sử điểm danh của một nhân viên bao gồm thông tin ca làm việc.
    """
    return get_attendance(db, employee_id)

@router.get("/check-today/{employee_id}")
def check_today_attendance(employee_id: int, db: Session = Depends(get_db)):
    """
    Kiểm tra xem nhân viên đã điểm danh hôm nay chưa
    """
    from app.models.employee import AttendanceRecord as AttendanceRecordModel
    
    today = date.today()
    existing = db.query(AttendanceRecordModel).filter(
        AttendanceRecordModel.employee_id == employee_id,
        func.date(AttendanceRecordModel.timestamp_in) == today
    ).first()
    
    if existing:
        return {
            "already_checked_in": True,
            "message": "Đã điểm danh hôm nay",
            "timestamp": existing.timestamp_in.isoformat(),
            "attendance_id": existing.id
        }
    else:
        return {
            "already_checked_in": False,
            "message": "Chưa điểm danh hôm nay",
            "timestamp": None,
            "attendance_id": None
        }

# API: Thống kê tổng số lượt điểm danh theo ngày/tháng
@router.get("/stats/summary")
def attendance_summary(
    db: Session = Depends(get_db),
    start_date: date = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: date = Query(None, description="Ngày kết thúc (YYYY-MM-DD)")
):
    """
    Thống kê tổng số lượt điểm danh theo ngày/tháng, có thể lọc theo khoảng thời gian.
    """
    q = db.query(
        func.date_trunc('day', AttendanceRecord.timestamp_in).label('day'),
        func.count().label('count')
    )
    if start_date:
        q = q.filter(AttendanceRecord.timestamp_in >= start_date)
    if end_date:
        q = q.filter(AttendanceRecord.timestamp_in <= end_date)
    q = q.group_by('day').order_by('day')
    result = q.all()
    return [{"day": str(row.day), "count": row.count} for row in result]
