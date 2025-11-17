
# FaceID Desktop App for Employee Lobby

Ứng dụng desktop giúp nhân viên quét FaceID tại sảnh, tích hợp AI nhận diện khuôn mặt và gửi kết quả lên backend.

## Tính năng
- Giao diện quét khuôn mặt bằng camera (PySide6)
- Nhận diện khuôn mặt bằng AI (face_recognition)
- **🔒 Anti-Spoofing** - Phát hiện giả mạo (ảnh in, video, màn hình)
- **😷 Mask Detection** - Phát hiện khẩu trang
- Gửi kết quả nhận diện lên backend để xác thực và điểm danh (requests)

## Cài đặt
1. Cài đặt Python >= 3.8
2. Cài các package:
   ```
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```
   python main.py
   ```

## ⚙️ Cấu hình Security

### Bật/Tắt Security Checks

Mở file `main.py` và tìm dòng (~388):

```python
ENABLE_SECURITY = False  # Đổi thành True để bật security
```

**Tắt security (Nhanh hơn, dễ test):**
```python
ENABLE_SECURITY = False
```

**Bật security (An toàn hơn):**
```python
ENABLE_SECURITY = True
```

### Điều chỉnh Thresholds

#### Anti-Spoofing (Chống giả mạo)
```python
anti_spoofing_detector = AntiSpoofing(threshold=0.50)
```

| Threshold | Khi nào dùng |
|-----------|--------------|
| 0.40-0.50 | Test/Development (dễ pass) |
| 0.50-0.60 | Production (cân bằng) |
| 0.60-0.70 | Bảo mật cao (khó pass) |

#### Mask Detection (Phát hiện khẩu trang)
```python
mask_detector = MaskDetector(threshold=0.65)
```

| Threshold | Khi nào dùng |
|-----------|--------------|
| 0.50-0.60 | Không nghiêm ngặt |
| 0.60-0.70 | Production (khuyến nghị) |
| 0.70-0.80 | Rất nghiêm ngặt |

## 🚀 Recommended Settings

### Development/Testing
```python
ENABLE_SECURITY = False  # Tắt để test nhanh
```

### Production (Văn phòng)
```python
ENABLE_SECURITY = True
anti_spoofing_detector = AntiSpoofing(threshold=0.50)
mask_detector = MaskDetector(threshold=0.65)
```

### Production (Bảo mật cao)
```python
ENABLE_SECURITY = True
anti_spoofing_detector = AntiSpoofing(threshold=0.65)
mask_detector = MaskDetector(threshold=0.70)
```

## 🔧 Troubleshooting

### Khuôn mặt thật bị chặn
**Triệu chứng:** "🚫 PHÁT HIỆN GIẢ MẠO!" với khuôn mặt thật

**Giải pháp:**
1. Bật thêm đèn (ánh sáng tốt hơn)
2. Đứng gần camera hơn (50-70cm)
3. Giảm threshold xuống 0.40
4. Hoặc tắt tạm: `ENABLE_SECURITY = False`

### Ảnh in vẫn pass được
**Triệu chứng:** Dùng ảnh in vẫn điểm danh được

**Giải pháp:**
1. Bật security: `ENABLE_SECURITY = True`
2. Tăng threshold lên 0.60+

### App chạy chậm / LAG 🐌
**Triệu chứng:** Camera lag, FPS thấp, CPU cao

**✅ ĐÃ TỐI ƯU:**
1. ✅ Skip frames: Chỉ detect face mỗi 3 frames (giảm 66% CPU)
2. ✅ Resize frame: 640x480 thay vì full HD (giảm 4x CPU)
3. ✅ Small detection: 320x240 cho face detection (giảm 4x CPU)
4. ✅ HOG model: Dùng HOG thay vì CNN (nhanh hơn 10x)
5. ✅ Small encoding: model='small' thay vì 'large' (nhanh hơn 5x)
6. ✅ Face resize: 150x150 thay vì 300x300 (nhanh hơn 4x)
7. ✅ FPS limit: 20 FPS thay vì 30+ FPS (giảm CPU)
8. ✅ Cache: Model & employee data chỉ load 1 lần

**Tổng cộng: Giảm ~80-90% CPU usage!**

**Nếu vẫn lag:**
1. Tắt security: `ENABLE_SECURITY = False` (giảm thêm 200ms/frame)
2. Đóng các app khác đang chạy
3. Upgrade CPU (khuyến nghị i5 trở lên)

## Quy trình sử dụng
1. Mở ứng dụng, nhấn nút "Quét FaceID".
2. Ứng dụng sẽ mở camera, chụp ảnh khuôn mặt nhân viên.
3. *(Nếu bật security)* Kiểm tra anti-spoofing và mask detection.
4. AI nhận diện khuôn mặt bằng thư viện face_recognition.
5. Gửi kết quả lên backend qua API (http://localhost:8000/api/faceid/scan).
6. Backend xác thực và trả về kết quả điểm danh.

## Lưu ý
- Đảm bảo máy tính có camera.
- Backend cần hỗ trợ API nhận diện khuôn mặt.
- **Security tắt mặc định** - Bật khi cần thiết.

## Liên hệ
Mọi thắc mắc hoặc góp ý vui lòng liên hệ nhóm phát triển.
