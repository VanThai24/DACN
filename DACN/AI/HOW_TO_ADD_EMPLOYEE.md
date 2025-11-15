# 👤 THÊM NHÂN VIÊN MỚI

## ❓ CÂU HỎI: Có cần train lại không?

**CÓ! Phải train lại khi thêm nhân viên mới.**

Model đã học 5 người cũ. Muốn nhận diện người thứ 6, phải train lại để model học thêm.

---

## ⚡ CÁCH NHANH NHẤT

### Option 1: Script tự động
```powershell
cd D:\DACN\DACN\AI
.\add_new_employee.bat
```

hoặc

```powershell
python add_new_employee.py
```

**Script sẽ tự động:**
1. ✅ Chụp ảnh nhân viên mới
2. ✅ Augment lên 40 ảnh
3. ✅ Retrain model
4. ✅ Update embeddings

**Thời gian:** ~10 phút

---

## 📋 HOẶC LÀM THỦ CÔNG (4 BƯỚC)

### Bước 1: Chụp ảnh
```powershell
python capture_training_data.py
# Tên: Minh (nhân viên mới)
# Số ảnh: 15-20
```

### Bước 2: Augment (optional nhưng khuyến nghị)
```powershell
python augment_data.py
# Chọn [1] - Augment 1 người
# Nhập: Minh
# Mục tiêu: 40
```

### Bước 3: Retrain model
```powershell
python train_best_model.py
```

### Bước 4: Update embeddings
```powershell
python update_embeddings_best_model.py
```

**Xong!**

---

## 🎯 KHI NÀO PHẢI TRAIN LẠI?

### ✅ PHẢI train lại:
- ➕ Thêm nhân viên mới
- 🔄 Cập nhật ảnh nhân viên cũ (thay đổi ngoại hình nhiều)
- 🗑️ Xóa nhân viên (optional, nhưng nên làm)

### ❌ KHÔNG cần train lại:
- 📊 Chỉ xem báo cáo/thống kê
- 🔍 Tìm kiếm attendance history
- ⚙️ Thay đổi settings (threshold, shift time, etc.)

---

## 💡 TIPS

### Tip 1: Chuẩn bị trước
Khi có nhân viên mới:
1. Chụp ảnh ngay (10-20 ảnh)
2. Augment về sau cũng được
3. Train 1 lần cho tất cả nhân viên mới

### Tip 2: Train hàng loạt
Nếu có nhiều nhân viên mới cùng lúc:
```powershell
# Chụp tất cả trước
python capture_training_data.py  # NV1
python capture_training_data.py  # NV2
python capture_training_data.py  # NV3

# Augment tất cả
python auto_augment.py

# Train 1 lần
python train_best_model.py
python update_embeddings_best_model.py
```

### Tip 3: Backup model cũ
```powershell
# Trước khi train lại
copy faceid_best_model.pkl faceid_best_model_backup.pkl
```

Nếu model mới không tốt, restore lại:
```powershell
copy faceid_best_model_backup.pkl faceid_best_model.pkl
```

---

## ⏱️ THỜI GIAN

| Bước | Thời gian | Ghi chú |
|------|-----------|---------|
| Chụp ảnh | 3-5 phút | 15-20 ảnh |
| Augment | 1 phút | Tự động |
| Train | 3-5 phút | Tùy số người |
| Update | 30 giây | Nhanh |
| **TỔNG** | **~10 phút** | |

---

## 📊 SỐ LƯỢNG ẢNH

### Tối thiểu (test nhanh):
- 10 ảnh gốc → Augment lên 30

### Khuyến nghị (cho đồ án):
- 15-20 ảnh gốc → Augment lên 40

### Tối ưu (production):
- 30-50 ảnh gốc (không cần augment nhiều)

---

## 🔄 QUY TRÌNH TỰ ĐỘNG

```powershell
# Chạy 1 lệnh, làm tất cả
cd D:\DACN\DACN\AI
.\add_new_employee.bat
```

**Script sẽ:**
1. Yêu cầu chụp ảnh
2. Tự động augment
3. Tự động train
4. Tự động update
5. Sẵn sàng test!

---

## ❓ FAQ

**Q: Train lại có mất model cũ không?**
A: Model cũ bị ghi đè. Nên backup trước.

**Q: Train lại có mất dữ liệu nhân viên cũ không?**
A: KHÔNG! Chỉ cập nhật model, data vẫn giữ nguyên.

**Q: Mất bao lâu?**
A: ~10 phút cho 1 nhân viên mới.

**Q: Có thể train offline không?**
A: CÓ! Tất cả đều chạy local.

**Q: Model mới có chính xác không?**
A: Nếu data đủ (40 ảnh/người), accuracy vẫn 85-90%.

---

🚀 **BẮT ĐẦU:** `.\add_new_employee.bat`
