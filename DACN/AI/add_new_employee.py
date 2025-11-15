"""
Script Python để thêm nhân viên mới
Tự động: Chụp → Augment → Train → Update
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Chạy command và hiển thị kết quả"""
    print(f"\n{'='*70}")
    print(f"🔄 {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ Lỗi: {description} thất bại!")
        return False
    
    print(f"\n✅ {description} thành công!")
    return True


def add_new_employee():
    """Quy trình thêm nhân viên mới"""
    
    print("\n" + "="*70)
    print("👤 THÊM NHÂN VIÊN MỚI VÀO HỆ THỐNG")
    print("="*70)
    print("Quy trình:")
    print("  1. Chụp ảnh nhân viên mới (15-20 ảnh)")
    print("  2. Augment data lên 40 ảnh")
    print("  3. Retrain model")
    print("  4. Update embeddings")
    print("\nThời gian: ~10 phút")
    print("="*70 + "\n")
    
    input("Nhấn Enter để bắt đầu...")
    
    # Bước 1: Chụp ảnh
    print("\n💡 Hướng dẫn chụp ảnh:")
    print("   - Nhập tên nhân viên (VD: Minh, Nam, Trang)")
    print("   - Nhập số ảnh: 15-20")
    print("   - Nhấn SPACE để chụp mỗi ảnh")
    print("   - Đa dạng góc độ")
    
    if not run_command("python capture_training_data.py", "Chụp ảnh nhân viên mới"):
        return False
    
    # Nhập tên nhân viên
    person_name = input("\n👤 Nhập lại tên nhân viên vừa chụp: ").strip()
    
    if not person_name:
        print("❌ Tên không được để trống!")
        return False
    
    # Bước 2: Augment
    print(f"\n🎨 Tăng cường dữ liệu cho {person_name}...")
    from augment_data import augment_person_data
    try:
        augment_person_data(person_name, 40)
    except Exception as e:
        print(f"⚠️  Augment warning: {e}")
        print("Tiếp tục với dữ liệu hiện có...")
    
    # Bước 3: Retrain
    if not run_command("python train_best_model.py", "Retrain model"):
        return False
    
    # Bước 4: Update embeddings
    if not run_command("python update_embeddings_best_model.py", "Update embeddings"):
        return False
    
    # Hoàn thành
    print("\n" + "="*70)
    print("✅ HOÀN TẤT! NHÂN VIÊN MỚI ĐÃ ĐƯỢC THÊM VÀO HỆ THỐNG")
    print("="*70)
    print(f"\nNhân viên: {person_name}")
    print("\n🎯 Bước tiếp theo:")
    print("   1. Test Desktop app")
    print("   2. Hoặc thêm nhân viên khác")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = add_new_employee()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        sys.exit(1)
