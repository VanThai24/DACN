"""
Tạo dữ liệu augmentation từ ảnh có sẵn
Tự động tạo thêm 40-50 ảnh từ 5-10 ảnh gốc
"""

import cv2
import os
import numpy as np
from pathlib import Path
from glob import glob

try:
    from imgaug import augmenters as iaa
    HAS_IMGAUG = True
except ImportError:
    HAS_IMGAUG = False
    print("⚠️  imgaug chưa cài. Chạy: pip install imgaug")
    print("   Hoặc dùng augmentation cơ bản của OpenCV\n")


def augment_with_opencv(image):
    """Augmentation cơ bản bằng OpenCV (không cần imgaug)"""
    augmented = []
    h, w = image.shape[:2]
    
    # 1. Flip ngang
    augmented.append(cv2.flip(image, 1))
    
    # 2. Xoay ±5, ±10, ±15 độ
    for angle in [-15, -10, -5, 5, 10, 15]:
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        augmented.append(rotated)
    
    # 3. Thay đổi độ sáng
    for alpha in [0.7, 0.85, 1.15, 1.3]:
        bright = cv2.convertScaleAbs(image, alpha=alpha, beta=0)
        augmented.append(bright)
    
    # 4. Làm mờ nhẹ
    augmented.append(cv2.GaussianBlur(image, (5, 5), 0))
    
    # 5. Thêm nhiễu
    noise = np.random.normal(0, 10, image.shape).astype(np.uint8)
    noisy = cv2.add(image, noise)
    augmented.append(noisy)
    
    # 6. Điều chỉnh contrast
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl,a,b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    augmented.append(enhanced)
    
    return augmented


def augment_with_imgaug(image):
    """Augmentation nâng cao bằng imgaug"""
    seq = iaa.Sequential([
        iaa.Fliplr(0.5),  # Flip ngang 50%
        iaa.Affine(
            rotate=(-20, 20),  # Xoay ±20 độ
            scale=(0.9, 1.1),  # Scale 90-110%
            shear=(-5, 5)      # Shear ±5 độ
        ),
        iaa.Multiply((0.8, 1.2)),  # Độ sáng 80-120%
        iaa.GaussianBlur(sigma=(0, 1.0)),  # Blur
        iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),  # Nhiễu
        iaa.LinearContrast((0.8, 1.2))  # Contrast
    ])
    
    # Tạo nhiều biến thể
    augmented = []
    for _ in range(8):  # Tạo 8 biến thể từ mỗi ảnh
        aug_image = seq(image=image)
        augmented.append(aug_image)
    
    return augmented


def augment_person_data(person_name, target_count=50):
    """
    Tăng cường dữ liệu cho 1 người
    
    Args:
        person_name: Tên người (folder trong face_data)
        target_count: Số ảnh mục tiêu (mặc định 50)
    """
    base_dir = Path(__file__).parent
    person_dir = base_dir / 'face_data' / person_name
    
    if not person_dir.exists():
        print(f"❌ Không tìm thấy thư mục: {person_dir}")
        return
    
    # Lấy tất cả ảnh hiện có
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        image_files.extend(glob(str(person_dir / ext)))
    
    if not image_files:
        print(f"❌ Không có ảnh nào trong {person_dir}")
        return
    
    current_count = len(image_files)
    print(f"\n{'='*70}")
    print(f"🔄 TĂNG CƯỜNG DỮ LIỆU CHO: {person_name}")
    print(f"{'='*70}")
    print(f"📊 Số ảnh hiện tại: {current_count}")
    print(f"🎯 Số ảnh mục tiêu: {target_count}")
    print(f"➕ Cần tạo thêm: {max(0, target_count - current_count)}")
    print(f"{'='*70}\n")
    
    if current_count >= target_count:
        print("✅ Đã đủ dữ liệu!")
        return
    
    # Tạo thư mục augmented
    aug_dir = person_dir / 'augmented'
    aug_dir.mkdir(exist_ok=True)
    
    augmented_count = 0
    images_needed = target_count - current_count
    
    print("🔄 Đang tạo ảnh augmented...\n")
    
    for img_file in image_files:
        if augmented_count >= images_needed:
            break
        
        # Đọc ảnh
        image = cv2.imread(img_file)
        if image is None:
            continue
        
        # Chọn phương pháp augmentation
        if HAS_IMGAUG:
            augmented_images = augment_with_imgaug(image)
        else:
            augmented_images = augment_with_opencv(image)
        
        # Lưu các ảnh augmented
        base_name = Path(img_file).stem
        for i, aug_img in enumerate(augmented_images):
            if augmented_count >= images_needed:
                break
            
            save_path = aug_dir / f"aug_{base_name}_{i:02d}.jpg"
            cv2.imwrite(str(save_path), aug_img)
            augmented_count += 1
            
            if augmented_count % 10 == 0:
                print(f"✅ Đã tạo {augmented_count}/{images_needed} ảnh")
    
    print(f"\n{'='*70}")
    print(f"✅ HOÀN THÀNH!")
    print(f"📁 Ảnh gốc: {current_count} (trong {person_dir})")
    print(f"📁 Ảnh augmented: {augmented_count} (trong {aug_dir})")
    print(f"📊 TỔNG: {current_count + augmented_count} ảnh")
    print(f"{'='*70}\n")
    
    if current_count + augmented_count >= target_count:
        print("🎉 Đủ dữ liệu để train! Bước tiếp theo:")
        print("   1. python train_best_model.py")
        print("   2. python update_embeddings_best_model.py")
    else:
        print("⚠️  Vẫn thiếu dữ liệu. Khuyến nghị:")
        print("   - Chụp thêm vài ảnh gốc nữa")
        print("   - Hoặc tăng target_count trong script")


def augment_all_people(target_count=50):
    """Augment cho tất cả người trong face_data"""
    base_dir = Path(__file__).parent / 'face_data'
    
    if not base_dir.exists():
        print(f"❌ Không tìm thấy {base_dir}")
        return
    
    people = [d for d in base_dir.iterdir() if d.is_dir()]
    
    if not people:
        print("❌ Không có ai trong face_data!")
        return
    
    print(f"\n{'='*70}")
    print(f"🚀 AUGMENT CHO TẤT CẢ ({len(people)} người)")
    print(f"{'='*70}\n")
    
    for person_dir in people:
        augment_person_data(person_dir.name, target_count)
        print()


def main():
    print("\n" + "="*70)
    print("🎨 CÔNG CỤ TĂNG CƯỜNG DỮ LIỆU (DATA AUGMENTATION)")
    print("="*70)
    print("Tự động tạo thêm ảnh từ dữ liệu có sẵn")
    print("Phù hợp khi chỉ có ít ảnh gốc (5-10 ảnh)")
    print("="*70 + "\n")
    
    print("Chọn chức năng:")
    print("  [1] Augment cho 1 người cụ thể")
    print("  [2] Augment cho TẤT CẢ mọi người")
    print("  [0] Thoát")
    
    choice = input("\nNhập lựa chọn (0-2): ").strip()
    
    if choice == "1":
        person_name = input("\n👤 Nhập tên người: ").strip()
        if person_name:
            try:
                target = int(input("🎯 Số ảnh mục tiêu (mặc định 50): ") or "50")
            except:
                target = 50
            augment_person_data(person_name, target)
        else:
            print("❌ Tên không được để trống!")
    
    elif choice == "2":
        try:
            target = int(input("\n🎯 Số ảnh mục tiêu cho mỗi người (mặc định 50): ") or "50")
        except:
            target = 50
        augment_all_people(target)
    
    elif choice == "0":
        print("👋 Bye!")
    
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
