"""
Tạo dữ liệu training giả (fake/dummy) cho testing
Dùng khi chưa có đủ nhân viên thật
"""

import cv2
import os
import numpy as np
from pathlib import Path
import random


def create_dummy_face_data(num_people=5, images_per_person=40):
    """
    Tạo dữ liệu giả từ 1 người thật
    
    Args:
        num_people: Số người ảo cần tạo
        images_per_person: Số ảnh mỗi người
    """
    base_dir = Path(__file__).parent / 'face_data'
    
    # Tìm người có dữ liệu thật
    real_people = [d for d in base_dir.iterdir() if d.is_dir()]
    
    if not real_people:
        print("❌ Không có dữ liệu gốc nào!")
        print("💡 Hãy chụp ít nhất 10 ảnh cho 1 người trước:")
        print("   python capture_training_data.py")
        return
    
    # Lấy người đầu tiên làm template
    template_person = real_people[0]
    template_images = list(template_person.glob('*.jpg')) + \
                     list(template_person.glob('*.jpeg')) + \
                     list(template_person.glob('*.png'))
    
    if len(template_images) < 5:
        print(f"❌ {template_person.name} chỉ có {len(template_images)} ảnh!")
        print("💡 Cần ít nhất 5 ảnh để tạo dummy data")
        return
    
    print(f"\n{'='*70}")
    print(f"🎭 TẠO DỮ LIỆU GIẢ TỪ: {template_person.name}")
    print(f"{'='*70}")
    print(f"📊 Template có: {len(template_images)} ảnh")
    print(f"🎯 Sẽ tạo: {num_people} người ảo x {images_per_person} ảnh")
    print(f"{'='*70}\n")
    
    # Danh sách tên giả
    dummy_names = [
        "DummyNV_A", "DummyNV_B", "DummyNV_C", 
        "DummyNV_D", "DummyNV_E", "DummyNV_F",
        "DummyNV_G", "DummyNV_H"
    ]
    
    confirm = input(f"⚠️  Tạo {num_people} người GIẢ để test? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Đã hủy!")
        return
    
    for i in range(num_people):
        person_name = dummy_names[i] if i < len(dummy_names) else f"DummyNV_{i+1}"
        person_dir = base_dir / person_name
        person_dir.mkdir(exist_ok=True)
        
        print(f"\n🔄 Đang tạo {person_name}...")
        
        created = 0
        while created < images_per_person:
            # Chọn random 1 ảnh template
            template_img_path = random.choice(template_images)
            img = cv2.imread(str(template_img_path))
            
            if img is None:
                continue
            
            # Áp dụng transformations để tạo biến thể
            # (Khác nhau đủ để model học, nhưng vẫn giữ đặc điểm)
            
            # 1. Flip ngang (50%)
            if random.random() > 0.5:
                img = cv2.flip(img, 1)
            
            # 2. Xoay random ±20 độ
            angle = random.uniform(-20, 20)
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            img = cv2.warpAffine(img, M, (w, h))
            
            # 3. Thay đổi độ sáng
            alpha = random.uniform(0.7, 1.3)
            img = cv2.convertScaleAbs(img, alpha=alpha, beta=random.randint(-30, 30))
            
            # 4. Blur nhẹ
            if random.random() > 0.5:
                img = cv2.GaussianBlur(img, (5, 5), 0)
            
            # 5. Thêm nhiễu
            if random.random() > 0.5:
                noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
                img = cv2.add(img, noise)
            
            # 6. Crop random
            crop_pct = random.uniform(0.8, 1.0)
            new_h, new_w = int(h * crop_pct), int(w * crop_pct)
            start_h = random.randint(0, h - new_h)
            start_w = random.randint(0, w - new_w)
            img = img[start_h:start_h+new_h, start_w:start_w+new_w]
            img = cv2.resize(img, (w, h))
            
            # Lưu ảnh
            save_path = person_dir / f"img_{created:03d}.jpg"
            cv2.imwrite(str(save_path), img)
            created += 1
            
            if created % 10 == 0:
                print(f"  ✅ {created}/{images_per_person}")
        
        print(f"  ✅ Hoàn thành {person_name}: {created} ảnh")
    
    print(f"\n{'='*70}")
    print(f"✅ ĐÃ TẠO XONG {num_people} NGƯỜI GIẢ!")
    print(f"{'='*70}")
    print(f"⚠️  LƯU Ý: Đây là dữ liệu GIẢ để test hệ thống")
    print(f"         Trong production, phải dùng ảnh thật của nhân viên!")
    print(f"\n🔄 Bước tiếp theo:")
    print(f"   1. python check_data.py")
    print(f"   2. python train_best_model.py")
    print(f"   3. python update_embeddings_best_model.py")
    print(f"{'='*70}\n")


def main():
    print("\n" + "="*70)
    print("🎭 TẠO DỮ LIỆU GIẢ (DUMMY DATA) CHO TESTING")
    print("="*70)
    print("⚠️  Chỉ dùng cho mục đích DEMO/TEST")
    print("   Trong production phải dùng ảnh thật!")
    print("="*70 + "\n")
    
    try:
        num_people = int(input("Số người giả cần tạo (mặc định 5): ") or "5")
        images_per_person = int(input("Số ảnh mỗi người (mặc định 40): ") or "40")
    except:
        num_people = 5
        images_per_person = 40
    
    create_dummy_face_data(num_people, images_per_person)


if __name__ == "__main__":
    main()
