# 📸 HƯỚNG DẪN THU THẬP DỮ LIỆU TRAINING

## 🎯 MỤC TIÊU
Thu thập 30-50 ảnh cho mỗi nhân viên với đa dạng góc độ, ánh sáng, biểu cảm để tăng độ chính xác của AI lên 85-90%.

---

## 🚀 CÁCH 1: Dùng Tool Tự Động (KHUYẾN NGHỊ)

### Bước 1: Chạy script thu thập ảnh
```bash
cd D:\DACN\DACN\AI
python capture_training_data.py
```

### Bước 2: Làm theo hướng dẫn
1. Nhập tên người (VD: Huy, Phong, Thai)
2. Nhập số ảnh muốn chụp (khuyến nghị 50)
3. Nhấn **SPACE** để bắt đầu chụp
4. Làm theo hướng dẫn trên màn hình:
   - **10 ảnh đầu**: Nhìn thẳng vào camera
   - **10 ảnh tiếp**: Xoay đầu sang TRÁI
   - **10 ảnh tiếp**: Xoay đầu sang PHẢI
   - **10 ảnh tiếp**: Ngẩng đầu LÊN
   - **10 ảnh cuối**: Cúi đầu XUỐNG

### Bước 3: Retrain model
```bash
# Sau khi chụp xong cho TẤT CẢ nhân viên
python train_best_model.py
python update_embeddings_best_model.py
```

---

## 📷 CÁCH 2: Chụp Ảnh Thủ Công

### Option A: Dùng webcam laptop
```python
# Tạo script đơn giản
import cv2
import os

person_name = "Huy"  # Thay tên
os.makedirs(f"face_data/{person_name}", exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0

while count < 50:
    ret, frame = cap.read()
    cv2.imshow('Press SPACE to capture', frame)
    
    key = cv2.waitKey(1)
    if key == ord(' '):
        cv2.imwrite(f"face_data/{person_name}/img_{count:03d}.jpg", frame)
        count += 1
        print(f"Captured {count}/50")
    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
```

### Option B: Chụp bằng điện thoại
1. Chụp 30-50 ảnh selfie với các góc độ khác nhau
2. Chuyển ảnh về máy tính
3. Copy vào thư mục: `D:\DACN\DACN\AI\face_data\[Tên người]\`

---

## 🎨 YÊU CẦU ẢNH CHẤT LƯỢNG

### ✅ ẢNH TỐT (Good):
- Khuôn mặt chiếm 40-60% khung hình
- Ánh sáng đều, không bị tối hoặc sáng quá
- Rõ nét, không mờ
- Đa dạng góc độ: trái, phải, ngẩng, cúi
- Đa dạng biểu cảm: cười, nghiêm túc, bình thường
- Cả khi đeo kính và không đeo kính

### ❌ ẢNH XẤU (Bad):
- Mặt quá nhỏ hoặc quá gần
- Tối hoặc ngược sáng
- Bị mờ, bị che khuất
- Chỉ có 1 góc độ
- Chất lượng thấp

---

## 📊 CHECKLIST THU THẬP DỮ LIỆU

### Cho mỗi nhân viên, cần có:
- [ ] 5-8 ảnh: Nhìn thẳng, ánh sáng tốt
- [ ] 5-8 ảnh: Xoay đầu trái
- [ ] 5-8 ảnh: Xoay đầu phải
- [ ] 5-8 ảnh: Ngẩng đầu
- [ ] 5-8 ảnh: Cúi đầu
- [ ] 3-5 ảnh: Đeo kính (nếu có)
- [ ] 3-5 ảnh: Trong điều kiện ánh sáng khác nhau

**TỔNG: 30-50 ảnh/người**

---

## 🔄 QUY TRÌNH HOÀN CHỈNH

### 1. Thu thập ảnh cho tất cả nhân viên
```bash
python capture_training_data.py
# Làm với từng người: Huy, Phong, Phát, Quang, Thai, Thiện
```

### 2. Kiểm tra dữ liệu
```bash
# Xem số lượng ảnh mỗi người
dir face_data\*\*.jpg /s /b | find /c "Huy"
dir face_data\*\*.jpg /s /b | find /c "Phong"
# ... làm tương tự cho các người khác
```

### 3. Retrain model
```bash
cd D:\DACN\DACN\AI
python train_best_model.py
```

Output mong đợi:
```
Training SVM classifier...
Best parameters: {'C': 10, 'gamma': 'scale', 'kernel': 'rbf'}
Test accuracy: 95.0%
✅ Model saved successfully!
```

### 4. Update embeddings
```bash
python update_embeddings_best_model.py
```

### 5. Test lại hệ thống
```bash
cd ..\faceid_desktop
python main.py
```

---

## 📈 KẾT QUẢ MONG ĐỢI

### Trước khi thu thập thêm dữ liệu:
- Training data: 5-8 ảnh/người
- Accuracy: ~60-70%
- Threshold: 30% (quá thấp)
- Vấn đề: Nhận diện sai nhiều

### Sau khi thu thập đủ dữ liệu:
- Training data: 30-50 ảnh/người
- Accuracy: **85-95%**
- Threshold: **65-70%** (an toàn hơn)
- Kết quả: Nhận diện chính xác, ít false positive

---

## 💡 TIPS & TRICKS

### Tip 1: Điều kiện chụp đa dạng
- Chụp vào các thời điểm khác nhau trong ngày
- Thay đổi góc chiếu sáng
- Có cả ảnh trong nhà và ngoài trời (nếu có thể)

### Tip 2: Với người đeo kính
- 70% ảnh đeo kính
- 30% ảnh không đeo kính

### Tip 3: Balance data
Đảm bảo mỗi người có số lượng ảnh tương đương nhau (30-50 ảnh)

### Tip 4: Augmentation (Optional)
Nếu không đủ ảnh, có thể dùng augmentation:
```python
from imgaug import augmenters as iaa

seq = iaa.Sequential([
    iaa.Fliplr(0.5),  # Lật ngang
    iaa.Affine(rotate=(-10, 10)),  # Xoay ±10°
    iaa.Multiply((0.8, 1.2)),  # Thay đổi độ sáng
])
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **Không copy ảnh từ internet**: Model sẽ overfitting
2. **Đảm bảo chỉ có 1 người trong ảnh**: Tránh nhiễu
3. **Xóa ảnh xấu**: Ảnh mờ, tối, bị che khuất
4. **Backup dữ liệu**: Lưu folder face_data vào nơi an toàn

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Không thể mở webcam"
```bash
# Kiểm tra webcam
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Thử camera index khác (nếu có nhiều camera)
# Sửa trong capture_training_data.py: cv2.VideoCapture(1)
```

### Lỗi: "Module cv2 not found"
```bash
pip install opencv-python
```

### Model accuracy vẫn thấp sau khi retrain
- Kiểm tra lại chất lượng ảnh
- Đảm bảo mỗi người có đủ 30+ ảnh
- Xóa ảnh xấu, ảnh bị nhiễu
- Chụp thêm ảnh trong điều kiện đa dạng hơn

---

## 📞 SUPPORT

Nếu gặp vấn đề, check:
1. Logs trong terminal
2. File `AI/train_best_model.py` - xem training process
3. Test với `faceid_desktop/main.py`

**Good luck! 🚀**
