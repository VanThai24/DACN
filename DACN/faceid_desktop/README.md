
# FaceID Desktop App for Employee Lobby

Ứng dụng desktop giúp nhân viên quét FaceID tại sảnh, tích hợp AI nhận diện khuôn mặt và gửi kết quả lên backend.

## Tính năng
- Giao diện quét khuôn mặt bằng camera (PySide6)
- Nhận diện khuôn mặt bằng AI (face_recognition)
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

## Quy trình sử dụng
1. Mở ứng dụng, nhấn nút "Quét FaceID".
2. Ứng dụng sẽ mở camera, chụp ảnh khuôn mặt nhân viên.
3. AI nhận diện khuôn mặt bằng thư viện face_recognition.
4. Nếu phát hiện khuôn mặt, mã hóa khuôn mặt sẽ được gửi lên backend qua API (mặc định: http://localhost:8000/api/faceid/scan).
5. Backend xác thực và trả về kết quả điểm danh.

## Tùy chỉnh
- Đổi địa chỉ backend trong hàm scan_face nếu cần.
- Có thể mở rộng để lưu lịch sử quét, hiển thị thông tin nhân viên, v.v.

## Lưu ý
- Đảm bảo máy tính có camera.
- Backend cần hỗ trợ API nhận diện khuôn mặt.

## Liên hệ
Mọi thắc mắc hoặc góp ý vui lòng liên hệ nhóm phát triển.
