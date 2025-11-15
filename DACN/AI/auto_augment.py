"""
Auto augment tất cả người trong face_data
Không cần input, chạy tự động
"""

import os
import sys
from pathlib import Path

# Import từ augment_data.py
sys.path.insert(0, str(Path(__file__).parent))
from augment_data import augment_person_data

def auto_augment_all(target_count=40):
    """Tự động augment tất cả người"""
    base_dir = Path(__file__).parent / 'face_data'
    
    if not base_dir.exists():
        print(f"❌ Không tìm thấy {base_dir}")
        return False
    
    people = sorted([d for d in base_dir.iterdir() if d.is_dir()])
    
    if not people:
        print("❌ Không có ai trong face_data!")
        return False
    
    print(f"\n{'='*70}")
    print(f"🚀 AUTO AUGMENT CHO {len(people)} NGƯỜI")
    print(f"🎯 Mục tiêu: {target_count} ảnh/người")
    print(f"{'='*70}\n")
    
    success_count = 0
    for person_dir in people:
        try:
            augment_person_data(person_dir.name, target_count)
            success_count += 1
        except Exception as e:
            print(f"❌ Lỗi khi augment {person_dir.name}: {e}")
            continue
    
    print(f"\n{'='*70}")
    print(f"✅ HOÀN TẤT! Đã augment {success_count}/{len(people)} người")
    print(f"{'='*70}\n")
    
    return success_count == len(people)


if __name__ == "__main__":
    success = auto_augment_all(target_count=40)
    
    if success:
        print("🎉 Dữ liệu đã sẵn sàng!")
        print("\n🔄 Tiếp theo:")
        print("   python train_best_model.py")
    else:
        print("⚠️  Có lỗi xảy ra. Check logs ở trên.")
        sys.exit(1)
