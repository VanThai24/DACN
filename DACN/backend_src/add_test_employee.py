"""
Script để thêm tài khoản test nhân viên vào database
Chỉ tài khoản có role='employee' mới đăng nhập được vào mobile app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend_src.app.database import SessionLocal
from backend_src.app.models.employee import Employee
from backend_src.app.models.user import User
import bcrypt
from datetime import datetime

def add_test_employee():
    db = SessionLocal()
    try:
        # Kiểm tra xem tài khoản test đã tồn tại chưa
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("❌ Tài khoản 'testuser' đã tồn tại!")
            print(f"   Username: testuser")
            print(f"   Role: {existing_user.role}")
            
            # Cập nhật mật khẩu nếu cần
            choice = input("\nBạn có muốn reset mật khẩu thành '123456'? (y/n): ")
            if choice.lower() == 'y':
                hashed = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())
                existing_user.password_hash = hashed.decode('utf-8')
                db.commit()
                print("✅ Đã reset mật khẩu thành công!")
            return
        
        # Tạo nhân viên mới
        print("\n📝 Tạo nhân viên test...")
        employee = Employee(
            name="Nguyễn Văn Test",
            department="Phòng IT",
            role="Nhân viên",
            phone="0123456789",
            email="testuser@company.com",
            is_locked=0
        )
        db.add(employee)
        db.flush()  # Để lấy employee.id
        
        print(f"✅ Đã tạo nhân viên: {employee.name} (ID: {employee.id})")
        
        # Hash mật khẩu với bcrypt
        password = "123456"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Tạo user với role='employee' (CHỈ role này mới đăng nhập mobile app được)
        print("\n🔐 Tạo tài khoản đăng nhập...")
        user = User(
            username="testuser",
            password_hash=hashed_password.decode('utf-8'),
            role="employee",  # QUAN TRỌNG: Phải là 'employee' để login mobile
            employee_id=employee.id
        )
        db.add(user)
        db.commit()
        
        print("\n" + "="*60)
        print("✅ TẠO TÀI KHOẢN TEST THÀNH CÔNG!")
        print("="*60)
        print(f"👤 Tên nhân viên: {employee.name}")
        print(f"🏢 Phòng ban: {employee.department}")
        print(f"💼 Chức vụ: {employee.role}")
        print(f"📞 SĐT: {employee.phone}")
        print(f"📧 Email: {employee.email}")
        print("\n🔑 THÔNG TIN ĐĂNG NHẬP MOBILE APP:")
        print(f"   Username: testuser")
        print(f"   Password: 123456")
        print(f"   Role: employee")
        print("="*60)
        print("\n⚠️  LƯU Ý: Chỉ tài khoản có role='employee' mới đăng nhập mobile app!")
        print("   Tài khoản admin KHÔNG thể đăng nhập mobile app.\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🚀 Đang thêm tài khoản test nhân viên vào database...")
    add_test_employee()
