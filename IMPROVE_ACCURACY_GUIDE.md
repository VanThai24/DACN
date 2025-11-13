# HƯỚNG DẪN CẢI THIỆN ĐỘ CHÍNH XÁC MODEL

## 🎯 Mục Tiêu
Nâng độ chính xác từ **55% → 90%+**

## 📊 Tình Trạng Hiện Tại

### ❌ Vấn Đề:
- Validation Accuracy: **83.33%** (trên 6 ảnh - không đại diện)
- Real-world Similarity: **< 60%** (quá thấp)
- Threshold hiện tại: **45%** (quá thấp, dễ nhận nhầm)
- Dữ liệu training: **Chỉ 7-9 ảnh/người** (quá ít!)

### ✅ Kết Quả Mong Muốn:
- Validation Accuracy: **≥ 95%**
- Real-world Similarity: **≥ 70%** cho người đúng
- Threshold: **60-70%** (an toàn)
- Dữ liệu training: **30-50 ảnh/người**

---

## 📝 QUY TRÌNH CẢI THIỆN (5 BƯỚC)

### BƯỚC 1: Thu Thập Dữ Liệu Lại 📸

**Chạy tool thu thập dữ liệu:**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe collect_face_data.py
```

**Hướng dẫn thu thập:**

1. **Chọn option 2** - Thu thập thêm cho người đã có
2. **Mỗi người cần:** 30-50 ảnh (tối thiểu 20)
3. **Đa dạng hóa:**
   - ✅ Góc độ: thẳng, nghiêng trái/phải, ngẩng/cúi nhẹ
   - ✅ Biểu cảm: tự nhiên, cười, nghiêm túc
   - ✅ Ánh sáng: sáng, tối, ánh sáng từ nhiều phía
   - ✅ Phụ kiện: có/không kính, khẩu trang
   - ✅ Khoảng cách: gần, xa

**Ví dụ:**
```
Menu chọn: 2
Nhập tên: Huy
Số ảnh: 40
→ Nhấn SPACE để chụp, thay đổi góc/biểu cảm sau mỗi lần
```

**Lặp lại cho tất cả 6 người:**
- Huy: thêm 40 ảnh (tổng ~47)
- Phong: thêm 40 ảnh (tổng ~48)
- Phát: thêm 40 ảnh (tổng ~49)
- Quang: thêm 40 ảnh (tổng ~48)
- Thai: thêm 40 ảnh (tổng ~47)
- Thiện: thêm 40 ảnh (tổng ~47)

---

### BƯỚC 2: Kiểm Tra Dữ Liệu 🔍

**Xem dữ liệu đã thu thập:**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe collect_face_data.py
# Chọn option 3 - Xem dữ liệu
```

**Kết quả mong muốn:**
```
✅ Huy        : 47 ảnh
✅ Phong      : 48 ảnh
✅ Phát       : 49 ảnh
✅ Quang      : 48 ảnh
✅ Thai       : 47 ảnh
✅ Thiện      : 47 ảnh
================================
Tổng: 6 người, 286 ảnh
```

---

### BƯỚC 3: Train Lại Model 🚀

**Chạy training với dữ liệu mới:**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe train_ai_optimized.py
```

**Theo dõi training:**
- Thời gian: ~15-20 phút (nhiều data hơn)
- Validation accuracy mục tiêu: **≥ 95%**

**Kết quả mong đợi:**
```
Validation Accuracy: 95-98%
Training samples: ~230
Validation samples: ~56
```

---

### BƯỚC 4: Đánh Giá Model 📊

**Chạy evaluation:**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe evaluate_model_accuracy.py
```

**Kiểm tra:**
- Overall Accuracy: **≥ 95%**
- Per-class Precision/Recall: **≥ 90%** cho mỗi người
- Confusion Matrix: ít nhầm lẫn
- Confidence: người đúng có confidence **≥ 70%**

---

### BƯỚC 5: Cập Nhật Database & Test 🔄

#### 5.1. Export Embedding Model
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe export_embedding_model.py
```

#### 5.2. Cập Nhật Embeddings vào Database

**Tạo script update embeddings:**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe update_embeddings_to_db.py
```

Script này sẽ:
1. Load model mới
2. Extract embeddings cho tất cả ảnh trong face_data
3. Cập nhật vào MySQL database

#### 5.3. Test Desktop App

**Chạy desktop:**
```powershell
cd D:\DACN\DACN\faceid_desktop
D:\DACN\.venv\Scripts\python.exe main.py
```

**Test với từng người:**
- Similarity mong đợi: **≥ 70%** cho người đúng
- Similarity người khác: **< 50%**

---

## 🔧 Điều Chỉnh Threshold

Sau khi test, điều chỉnh threshold trong `main.py`:

**Nếu accuracy cao (≥ 95%):**
```python
THRESHOLD = 0.65  # Chặt chẽ hơn
```

**Nếu cần balance:**
```python
THRESHOLD = 0.60  # Cân bằng
```

**Công thức tính threshold tối ưu:**
```
Threshold = (min_similarity_correct + max_similarity_wrong) / 2
```

---

## 📈 Monitoring & Validation

### Checklist Trước Khi Deploy:

- [ ] Mỗi người có ≥ 30 ảnh
- [ ] Validation accuracy ≥ 95%
- [ ] Test với 10 lần quét mỗi người → đúng ≥ 9/10 lần
- [ ] Không có false positive (người lạ được nhận diện)
- [ ] Confidence ổn định (không dao động quá 10%)

### Test Cases:

**Test 1: Người đúng**
```
Người: Huy
Kỳ vọng: "✅ Điểm danh: Huy (75%+)"
```

**Test 2: Người sai**
```
Người: Random person không trong DB
Kỳ vọng: "❌ Không nhận diện được"
```

**Test 3: Góc độ khác**
```
Người: Thai (nghiêng 30°)
Kỳ vọng: Vẫn nhận diện đúng
```

**Test 4: Ánh sáng khác**
```
Người: Phát (ánh sáng yếu)
Kỳ vọng: Vẫn nhận diện đúng
```

---

## 🎓 Tips & Best Practices

### 1. Thu Thập Dữ Liệu

**✅ ĐÚNG:**
- Chụp từ nhiều góc độ khác nhau
- Thay đổi biểu cảm
- Thay đổi ánh sáng
- Khoảng cách camera khác nhau

**❌ SAI:**
- Chụp cùng 1 góc độ
- Cùng 1 biểu cảm
- Cùng 1 điều kiện ánh sáng
- Ảnh bị mờ, tối

### 2. Training

**✅ Best Practices:**
- Dùng early stopping (đã có sẵn)
- Monitor validation loss
- Save best model (đã có sẵn)
- Data augmentation (đã có sẵn)

### 3. Threshold Tuning

**Nguyên tắc:**
- **High security**: Threshold cao (0.70-0.80) → ít false positive
- **User friendly**: Threshold thấp (0.55-0.65) → dễ nhận diện
- **Balanced**: Threshold trung bình (0.60-0.70) → cân bằng

**Công thức ROC:**
```
False Positive Rate (FPR) = False Positives / Total Negatives
False Negative Rate (FNR) = False Negatives / Total Positives

Tối ưu: FPR < 5%, FNR < 10%
```

---

## 🚨 Troubleshooting

### Vấn đề 1: Accuracy vẫn thấp sau khi train lại

**Nguyên nhân:**
- Dữ liệu vẫn chưa đủ đa dạng
- Model overfit

**Giải pháp:**
- Thu thập thêm data đa dạng hơn
- Tăng data augmentation
- Giảm model complexity

### Vấn đề 2: Desktop không nhận diện được

**Nguyên nhân:**
- Database chưa được cập nhật embeddings
- Model path sai

**Giải pháp:**
- Chạy lại `update_embeddings_to_db.py`
- Kiểm tra đường dẫn model trong `main.py`

### Vấn đề 3: Nhận nhầm người

**Nguyên nhân:**
- Threshold quá thấp
- 2 người có đặc điểm tương đồng

**Giải pháp:**
- Tăng threshold lên 0.65-0.70
- Thu thập thêm ảnh để model phân biệt rõ hơn

---

## 📞 Quick Commands

### Thu thập dữ liệu:
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe collect_face_data.py
```

### Train lại:
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe train_ai_optimized.py
```

### Đánh giá:
```powershell
cd D:\DACN\DACN\AI
D:\DACN\.venv\Scripts\python.exe evaluate_model_accuracy.py
```

### Test desktop:
```powershell
cd D:\DACN\DACN\faceid_desktop
D:\DACN\.venv\Scripts\python.exe main.py
```

---

## 🎯 Timeline Dự Kiến

| Bước | Thời gian | Mô tả |
|------|-----------|-------|
| 1. Thu thập data | 30-45 phút | 40 ảnh × 6 người |
| 2. Train model | 15-20 phút | Với ~286 ảnh |
| 3. Evaluate | 2-3 phút | Đánh giá accuracy |
| 4. Update DB | 5 phút | Cập nhật embeddings |
| 5. Test | 10 phút | Test từng người |
| **Tổng** | **~1.5 giờ** | Hoàn thiện hệ thống |

---

**BẮT ĐẦU NGAY:** Chạy `collect_face_data.py` để thu thập dữ liệu! 🚀
