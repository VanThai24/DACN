# FaceID AI v2.0 - Hướng dẫn sử dụng

## 🚀 Cải tiến so với version cũ

### Version cũ (Có vấn đề):
- ❌ **Kiến trúc**: Basic CNN (Conv2D 32-64-128)
- ❌ **Augmentation**: vertical_flip=True (mặt lộn ngược), rotation_range=60 (quá nhiều)
- ❌ **Image size**: 128x128 (nhỏ, thiếu chi tiết)
- ❌ **Distance metric**: Euclidean distance
- ❌ **Threshold**: 10.0 (quá lỏng, nhiều false positive)
- ❌ **Normalization**: Không có

### Version mới (Cải tiến):
- ✅ **Kiến trúc**: MobileNetV2 Transfer Learning (pre-trained trên ImageNet)
- ✅ **Augmentation**: Chỉ horizontal_flip, rotation_range=20 (phù hợp khuôn mặt)
- ✅ **Image size**: 160x160 (đủ chi tiết)
- ✅ **Distance metric**: **Cosine Similarity** (chính xác hơn)
- ✅ **Threshold**: 0.65 similarity (strict, ít false positive)
- ✅ **Normalization**: L2 normalized embeddings

## 📊 Kết quả mong đợi

| Metric | Version cũ | Version mới |
|--------|-----------|-------------|
| Accuracy | ~60-70% | **>90%** |
| False Positive | Cao (threshold 10.0) | Thấp (threshold 0.65) |
| Training time | 20-30 phút | 30-60 phút |
| Model size | 5 MB | 12 MB |

## 🔧 Cách sử dụng

### 1. Train model mới

```powershell
cd D:\DACN\DACN\AI
D:\DACN\DACN\venv\Scripts\python.exe train_faceid_improved_v2.py
```

**Output mong đợi:**
- Phase 1: Train 20 epochs với base frozen → val_accuracy ~50-70%
- Phase 2: Fine-tune 30 epochs → val_accuracy **>90%**
- Lưu best model tại: `faceid_model_tf_best.h5`

### 2. Khởi động Flask server

**Cách 1: Dùng script tự động**
```powershell
cd D:\DACN\DACN\AI
.\start_server.ps1
```

**Cách 2: Chạy trực tiếp**
```powershell
cd D:\DACN\DACN\AI
D:\DACN\DACN\venv\Scripts\python.exe app.py
```

Server sẽ chạy tại: `http://127.0.0.1:5000`

### 3. Test API

**Scan khuôn mặt:**
```bash
POST http://127.0.0.1:5000/scan
Content-Type: multipart/form-data
Body: image (file)
```

**Response thành công:**
```json
{
  "success": true,
  "result": "Match",
  "id": 34,
  "name": "Nguyễn Văn A",
  "similarity": 0.89,
  "distance": 0.11,
  "confidence": 89.0
}
```

**Response không khớp:**
```json
{
  "success": false,
  "result": "No match",
  "reason": "Face not recognized",
  "best_similarity": 0.45,
  "best_distance": 0.55,
  "threshold": 0.65
}
```

### 4. Thêm khuôn mặt mới

```bash
POST http://127.0.0.1:5000/add_face
Content-Type: multipart/form-data
Body: 
  - image (file)
  - name (string)
```

## ⚙️ Cấu hình threshold

Trong file `app.py` (hoặc `app_improved.py`):

```python
# Threshold cao = strict hơn (ít false positive)
SIMILARITY_THRESHOLD = 0.65  # Mặc định: 0.65
DISTANCE_THRESHOLD = 0.35    # Hoặc dùng distance

# Điều chỉnh theo nhu cầu:
# - 0.70-0.80: Rất strict (chỉ khớp khi giống >70%)
# - 0.60-0.70: Vừa phải (khuyến nghị)
# - 0.50-0.60: Lỏng hơn (nhiều false positive)
```

## 🔍 Debugging

### Xem log khi scan:

```python
# Server sẽ in ra:
[DEBUG] Loaded 6 embeddings from database
[DEBUG] Nguyễn Văn A (ID 34): similarity = 0.8945, distance = 0.1055
[DEBUG] Trần Văn B (ID 35): similarity = 0.3421, distance = 0.6579
[DEBUG] Best match: Nguyễn Văn A (ID 34)
[DEBUG] Similarity: 0.8945, Distance: 0.1055
```

### Kiểm tra model đã load:

```bash
GET http://127.0.0.1:5000/
```

Response:
```json
{
  "status": "running",
  "message": "FaceID API v2.0 - Improved with Transfer Learning",
  "model": "MobileNetV2 + L2 Normalization",
  "similarity_method": "Cosine Similarity"
}
```

## 📁 File structure

```
AI/
├── app.py                          # Server chính (đã update cosine similarity)
├── app_improved.py                 # Backup version mới
├── app_old.py                      # Backup version cũ
├── train_faceid_improved_v2.py     # Script train mới
├── train_faceid_tensorflow.py      # Script train cũ
├── faceid_model_tf_best.h5         # Model tốt nhất (từ ModelCheckpoint)
├── faceid_model_tf.h5              # Model cuối cùng
├── start_server.ps1                # Script khởi động tự động
├── db.py                           # Database connection
└── face_data/                      # Training images
    ├── Huy/
    ├── Phát/
    ├── Phong/
    ├── Quang/
    ├── Thai/
    └── Thiện/
```

## 🎯 Tips để có accuracy cao

1. **Ảnh training chất lượng cao**:
   - Nhiều góc độ khác nhau
   - Ánh sáng đủ (không quá tối/sáng)
   - Mặt thẳng + nghiêng nhẹ
   - Nhiều biểu cảm (cười, nghiêm túc, etc.)

2. **Số lượng ảnh mỗi người**: 
   - Tối thiểu: 5-10 ảnh
   - Khuyến nghị: 15-20 ảnh
   - Tối ưu: 30+ ảnh

3. **Điều chỉnh threshold**:
   - Test với ảnh thật → Xem similarity score
   - Nếu similarity của người đúng < 0.65 → Giảm threshold
   - Nếu có false positive → Tăng threshold

4. **Re-train khi thêm người mới**:
   - Thêm folder mới vào `face_data/`
   - Chạy lại `train_faceid_improved_v2.py`
   - Restart Flask server

## 🚨 Troubleshooting

### Lỗi: "No model found"
```powershell
# Train model trước
python train_faceid_improved_v2.py
```

### Lỗi: "Cannot decode embedding"
- Database có embedding cũ (từ model cũ)
- Giải pháp: Re-scan tất cả khuôn mặt với model mới

### Accuracy vẫn thấp sau khi train
1. Kiểm tra số lượng ảnh training (mỗi người >= 10 ảnh)
2. Kiểm tra chất lượng ảnh (rõ nét, đủ sáng)
3. Xem validation accuracy trong log training
4. Điều chỉnh threshold phù hợp

## 📞 Support

Nếu gặp vấn đề:
1. Check log trong terminal
2. Test API qua Postman/curl
3. Xem file log trong `AI/` folder
