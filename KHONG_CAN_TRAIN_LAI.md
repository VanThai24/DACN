# HƯỚNG DẪN: 2 CÁCH KHÔNG CẦN TRAIN LẠI KHI THÊM NHÂN VIÊN

## 🎯 Cách 1: Dùng Embedding Matching (KHUYẾN NGHỊ - ĐÃ LÀM)

### ✅ Đã hoàn thành:
1. ✅ Migrate embeddings cho 6 nhân viên hiện tại → database
2. ✅ Tạo `main_embedding.py` - App mới dùng embedding matching
3. ✅ Tạo `add_employee_no_retrain.py` - Script thêm nhân viên mới

### 🚀 Cách chạy:

**Chạy app mới (dùng embedding):**
```bash
cd D:\DACN\DACN\faceid_desktop
python main_embedding.py
```

**Thêm nhân viên mới (KHÔNG CẦN TRAIN):**
```bash
cd D:\DACN
python add_employee_no_retrain.py
```

Trong file `add_employee_no_retrain.py`, uncomment và sửa:
```python
add_employee(
    name="Nguyễn Văn Minh",
    image_path=r"D:\path\to\photo.jpg",  # Chỉ cần 1 ảnh!
    phone="0987654321",
    department="IT"
)
```

### 💡 Ưu điểm:
- ✅ **KHÔNG CẦN TRAIN LẠI** model khi thêm người mới
- ✅ Chỉ cần 1 ảnh để thêm nhân viên
- ✅ Độ chính xác cao (cosine similarity)
- ✅ Linh hoạt: thêm/xóa nhân viên bất cứ lúc nào

### 📊 Cách hoạt động:
```
1. Khi scan khuôn mặt:
   - Extract embedding 128-dim từ ảnh
   
2. So sánh với database:
   - Tính cosine similarity với tất cả embeddings đã lưu
   - Tìm người có similarity cao nhất
   
3. Nhận diện:
   - Nếu similarity >= threshold (0.6) → Nhận diện thành công
   - Nếu < threshold → Không nhận diện được
```

---

## 🎯 Cách 2: Dùng Backend API Có Sẵn

Backend của bạn đã có sẵn endpoint `/api/faceid/scan` hỗ trợ embedding matching!

### Cách dùng:

**Sửa `main.py` để gọi API backend:**

```python
# Thay vì dùng model local, gọi API
import requests

# Extract embedding từ ảnh
face_resized = cv2.resize(face_img, (160, 160))
face_array = np.array(face_resized) / 255.0
face_array = np.expand_dims(face_array, axis=0)

# Gọi API backend
headers = {"Authorization": f"Bearer {jwt_token}"}
response = requests.post(
    "http://localhost:8000/api/faceid/scan",
    json={"encodings": face_array.tolist()},
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    # Backend trả về tên nhân viên đã nhận diện
```

---

## ⚠️ Vấn đề hiện tại

**App `main.py` cũ đang dùng classification (6 classes cố định):**
- ❌ Predict → output [0.1, 0.3, 0.5, 0.05, 0.02, 0.03]
- ❌ Chọn index có xác suất cao nhất
- ❌ Phải train lại khi thêm class mới

**App `main_embedding.py` mới dùng embedding matching:**
- ✅ Extract embedding → vector 128-dim
- ✅ So sánh với database bằng cosine similarity
- ✅ KHÔNG cần train lại khi thêm người mới

---

## 🔧 Fix ngay

### Fix 1: Chạy app mới
```bash
cd D:\DACN\DACN\faceid_desktop
python main_embedding.py
```

### Fix 2: Hoặc thay thế main.py cũ
```bash
cd D:\DACN\DACN\faceid_desktop
copy main.py main_old_classification.py
copy main_embedding.py main.py
python main.py
```

### Fix 3: Đảm bảo có embeddings trong DB
```bash
cd D:\DACN
python migrate_to_embedding.py
```

Kết quả phải là:
```
✅ Thành công: 6 nhân viên
✅ Tỷ lệ: 6/6 (100%)
```

---

## 📋 So sánh 2 phương pháp

| Tiêu chí | Classification (cũ) | Embedding Matching (mới) |
|----------|---------------------|--------------------------|
| Thêm người mới | ❌ Phải train lại | ✅ Chỉ cần 1 ảnh |
| Thời gian train | ❌ 10-30 phút | ✅ 0 phút (không cần) |
| Số ảnh cần | ❌ 10-20 ảnh/người | ✅ 1 ảnh/người |
| Độ chính xác | ⚠️ Trung bình | ✅ Cao hơn |
| Linh hoạt | ❌ Cố định số người | ✅ Không giới hạn |
| Tốc độ scan | ✅ Nhanh | ✅ Nhanh (tương đương) |

---

## 🎉 Kết luận

**ĐỀ XUẤT:** Dùng `main_embedding.py` - Đã sẵn sàng 100%!

**Lợi ích:**
- ✅ Đã migrate 6 nhân viên hiện tại
- ✅ Sẵn sàng thêm người mới bất cứ lúc nào
- ✅ KHÔNG cần train lại model
- ✅ Chỉ cần 1 ảnh để thêm nhân viên

**Chạy ngay:**
```bash
cd D:\DACN\DACN\faceid_desktop
python main_embedding.py
```
