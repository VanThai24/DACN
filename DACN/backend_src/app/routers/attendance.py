
from fastapi import APIRouter, Depends, HTTPException, Query
from backend_src.app.database import SessionLocal
from backend_src.app.schemas.employee import AttendanceRecord, AttendanceRecordCreate
from backend_src.app.crud.employee import get_attendance, create_attendance
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

@router.post("/", response_model=AttendanceRecord)
def create_attendance_api(attendance: AttendanceRecordCreate, db: Session = Depends(get_db)):
    """
    Ghi nhận một lượt điểm danh mới cho nhân viên.
    """
    return create_attendance(db, attendance)

@router.get("/employee/{employee_id}", response_model=list[AttendanceRecord])
def read_attendance(employee_id: int, db: Session = Depends(get_db)):
    """
    Lấy danh sách lịch sử điểm danh của một nhân viên.
    """
    return get_attendance(db, employee_id)

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
