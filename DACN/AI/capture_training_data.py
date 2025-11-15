"""
Script thu thập ảnh training cho Face Recognition
Chụp 50 ảnh tự động với hướng dẫn thay đổi góc độ
"""

import cv2
import os
import time
from datetime import datetime

def capture_training_images(person_name, num_images=50):
    """
    Thu thập ảnh training cho một người
    
    Args:
        person_name: Tên người (tạo folder với tên này)
        num_images: Số lượng ảnh cần chụp (mặc định 50)
    """
    # Tạo thư mục nếu chưa có
    save_dir = f"face_data/{person_name}"
    os.makedirs(save_dir, exist_ok=True)
    
    # Khởi tạo webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở webcam!")
        return
    
    # Cấu hình
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print(f"\n{'='*60}")
    print(f"📸 THU THẬP ẢNH TRAINING CHO: {person_name}")
    print(f"{'='*60}")
    print(f"Sẽ chụp {num_images} ảnh với các hướng dẫn:")
    print("  - 10 ảnh: Nhìn thẳng")
    print("  - 10 ảnh: Xoay đầu trái")
    print("  - 10 ảnh: Xoay đầu phải")
    print("  - 10 ảnh: Ngẩng đầu lên")
    print("  - 10 ảnh: Cúi đầu xuống")
    print("\n⌨️  Nhấn SPACE để bắt đầu, ESC để thoát")
    print(f"{'='*60}\n")
    
    # Các hướng dẫn
    instructions = [
        ("📷 Nhìn thẳng vào camera", 10),
        ("⬅️ Xoay đầu sang TRÁI", 10),
        ("➡️ Xoay đầu sang PHẢI", 10),
        ("⬆️ Ngẩng đầu LÊN", 10),
        ("⬇️ Cúi đầu XUỐNG", 10)
    ]
    
    count = 0
    instruction_index = 0
    images_in_current_pose = 0
    started = False
    
    # Face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không đọc được frame!")
            break
        
        # Lật ảnh để dễ nhìn
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Vẽ khung và thông tin
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Face Detected", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Hiển thị hướng dẫn
        if instruction_index < len(instructions):
            instruction, target = instructions[instruction_index]
            status_text = f"{instruction} ({images_in_current_pose}/{target})"
        else:
            status_text = "HOÀN THÀNH!"
        
        # Overlay thông tin
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        cv2.putText(frame, status_text, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Tong: {count}/{num_images}", (20, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        if not started:
            cv2.putText(frame, "Nhan SPACE de bat dau", (20, frame.shape[0]-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        cv2.imshow('Thu thap anh training - Nhan ESC de thoat', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Space để bắt đầu
        if key == ord(' '):
            if not started:
                started = True
                print("\n▶️  Bắt đầu chụp ảnh...")
            
            # Chụp ảnh nếu phát hiện được mặt
            if len(faces) > 0 and started:
                # Lấy khuôn mặt lớn nhất
                x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
                
                # Crop face với margin
                margin = 30
                y1 = max(0, y - margin)
                y2 = min(frame.shape[0], y + h + margin)
                x1 = max(0, x - margin)
                x2 = min(frame.shape[1], x + w + margin)
                face_img = frame[y1:y2, x1:x2]
                
                # Lưu ảnh
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                pose_name = instructions[instruction_index][0].split()[0]
                filename = f"{save_dir}/{pose_name}_{count+1:03d}_{timestamp}.jpg"
                cv2.imwrite(filename, face_img)
                
                count += 1
                images_in_current_pose += 1
                print(f"✅ Đã chụp {count}/{num_images}: {filename}")
                
                # Chuyển sang pose tiếp theo
                if images_in_current_pose >= instructions[instruction_index][1]:
                    instruction_index += 1
                    images_in_current_pose = 0
                    if instruction_index < len(instructions):
                        print(f"\n🔄 Chuyển sang: {instructions[instruction_index][0]}")
                
                # Delay nhỏ để tránh chụp quá nhanh
                time.sleep(0.3)
        
        # ESC để thoát
        elif key == 27:
            print("\n⚠️  Đã hủy bỏ!")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if count >= num_images:
        print(f"\n{'='*60}")
        print(f"✅ HOÀN THÀNH! Đã chụp {count} ảnh cho {person_name}")
        print(f"📁 Lưu tại: {save_dir}")
        print(f"{'='*60}\n")
        print("🔄 Bước tiếp theo:")
        print("   1. Chạy: python train_best_model.py")
        print("   2. Chạy: python update_embeddings_best_model.py")
        print(f"{'='*60}\n")
    else:
        print(f"\n⚠️  Chỉ chụp được {count}/{num_images} ảnh")


def main():
    print("\n" + "="*60)
    print("🎯 CÔNG CỤ THU THẬP DỮ LIỆU TRAINING FACE RECOGNITION")
    print("="*60)
    
    person_name = input("\n👤 Nhập tên người (VD: Huy, Phong, Thai): ").strip()
    
    if not person_name:
        print("❌ Tên không được để trống!")
        return
    
    try:
        num_images = int(input("📸 Số lượng ảnh muốn chụp (khuyến nghị 50): ") or "50")
    except ValueError:
        num_images = 50
    
    if num_images < 20:
        print("⚠️  Khuyến nghị chụp ít nhất 30-50 ảnh để model chính xác hơn")
    
    confirm = input(f"\n✅ Sẽ chụp {num_images} ảnh cho {person_name}. Tiếp tục? (y/n): ")
    
    if confirm.lower() == 'y':
        capture_training_images(person_name, num_images)
    else:
        print("❌ Đã hủy!")


if __name__ == "__main__":
    main()
