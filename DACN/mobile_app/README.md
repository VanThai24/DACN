# Mobile App - Hệ thống Điểm danh FaceID

## 📱 Giới thiệu

Ứng dụng mobile dành cho nhân viên để xem lịch sử điểm danh, thống kê chấm công và quản lý thông tin cá nhân.

## ✨ Tính năng chính

### 🏠 Trang chủ (HomeScreen)
- Hiển thị thông tin nhân viên (tên, phòng ban, avatar)
- Thống kê nhanh về điểm danh trong tháng:
  - Số ngày đã điểm danh
  - Số lần đúng giờ / trễ giờ
  - Tỷ lệ đúng giờ (%)
- Loading state với ActivityIndicator
- Giao diện đẹp với gradient background

### 📅 Lịch sử điểm danh (AttendanceScreen)
- Danh sách bản ghi điểm danh với format thời gian đẹp (DD/MM/YYYY HH:mm)
- **Pull-to-refresh**: Kéo xuống để làm mới dữ liệu
- **Xem chi tiết**: Nhấn vào bản ghi để xem modal chi tiết:
  - Thời gian vào/ra đầy đủ
  - Trạng thái (in/out)
  - Thiết bị điểm danh
- Thống kê tổng quan:
  - Ngày điểm danh trong tháng/quý
  - Số lần đúng giờ/trễ
  - Số ngày vắng
- Icon màu sắc trực quan cho từng loại thông tin

### 👤 Thông tin cá nhân (ProfileScreen)
- Hiển thị đầy đủ thông tin: Họ tên, phòng ban, chức vụ, SĐT, email
- **Cập nhật số điện thoại**: Nhấn icon edit bên cạnh SĐT
- Avatar lớn với badge verified
- Nút đăng xuất với màu đỏ nổi bật
- Giao diện card đẹp với icons Material

### 🔐 Đăng nhập (LoginScreen)
- Form đăng nhập với username/password
- Loading indicator khi đang xử lý
- Kiểm tra kết nối server trước khi login
- Thông báo lỗi rõ ràng

## 🛠 Cải tiến đã thực hiện

### UX/UI
- ✅ Loading states cho tất cả API calls
- ✅ Pull-to-refresh cho danh sách
- ✅ Modal chi tiết với animation
- ✅ Icons Material Design đầy màu sắc
- ✅ Gradient background đẹp mắt
- ✅ Card shadows và elevations
- ✅ Format thời gian người dùng thân thiện

### Chức năng
- ✅ Xem chi tiết từng bản ghi điểm danh
- ✅ Cập nhật số điện thoại trực tiếp trong app
- ✅ Thống kê realtime từ API
- ✅ Tính toán tỷ lệ đúng giờ tự động
- ✅ Hiển thị avatar từ server hoặc fallback

### Code Quality
- ✅ Reusable functions (formatDateTime, getMonthStats, etc.)
- ✅ Error handling đầy đủ
- ✅ PropTypes với user object
- ✅ Consistent styling

## 📦 Cài đặt

```bash
cd mobile_app
npm install
```

## 🚀 Chạy ứng dụng

### Cấu hình server
Mở `config.js` và thay đổi IP server:
```javascript
export const SERVER_IP = "192.168.110.45"; // Đổi IP này
export const API_URL = `http://${SERVER_IP}:8000`;
```

### Chạy trên thiết bị thật hoặc emulator
```bash
# Android
npm run android

# iOS
npm run ios

# Web (development)
npm start
```

## 📱 Yêu cầu hệ thống

- Node.js >= 16
- Expo CLI
- React Native >= 0.81
- Android Studio (cho Android) hoặc Xcode (cho iOS)

## 🔌 API Endpoints sử dụng

- `POST /auth/login` - Đăng nhập
- `GET /attendance/employee/:id` - Lấy lịch sử điểm danh
- `PUT /employees/:id` - Cập nhật thông tin nhân viên

## 📸 Screenshots

### Trang chủ
- Header với avatar và tên nhân viên
- 4 card thống kê: Ngày điểm danh, Đúng giờ, Trễ giờ, Tỷ lệ %

### Điểm danh
- Danh sách bản ghi với icon login/logout
- Modal chi tiết khi nhấn vào bản ghi
- Pull-to-refresh animation

### Cá nhân
- Avatar tròn lớn với badge verified
- Các row thông tin với icons
- Icon edit bên cạnh SĐT để chỉnh sửa

## 🐛 Troubleshooting

### Không kết nối được server
1. Kiểm tra IP trong `config.js`
2. Đảm bảo thiết bị và server cùng mạng WiFi
3. Kiểm tra server đang chạy trên port 8000

### Không hiển thị avatar
- Server cần serve static files từ `/photos`
- Kiểm tra `photo_path` trong database có đúng format

### Pull-to-refresh không hoạt động
- Đảm bảo đã import RefreshControl từ react-native
- Kiểm tra FlatList có props refreshControl

## 📝 Tương lai

- [ ] Thêm dark mode
- [ ] Push notifications cho reminder điểm danh
- [ ] Chart/Graph thống kê theo tuần/tháng
- [ ] Camera để chụp avatar mới
- [ ] Offline mode với AsyncStorage
- [ ] Multi-language support (EN/VI)

## 👨‍💻 Developer Notes

### Cấu trúc thư mục
```
mobile_app/
├── screens/          # Các màn hình chính
│   ├── HomeScreen.js
│   ├── AttendanceScreen.js
│   ├── ProfileScreen.js
│   └── LoginScreen.js
├── components/       # Components tái sử dụng
├── config.js        # Cấu hình API
├── App.js           # Root component với navigation
└── package.json
```

### Style Guidelines
- Sử dụng màu chủ đạo: `#2979ff` (blue)
- Màu thành công: `#43a047` (green)
- Màu cảnh báo: `#e53935` (red)
- Border radius: 12-16px cho cards
- Padding: 16-20px standard

---

**Version**: 2.0  
**Last Updated**: 2025-01-12  
**Author**: DACN Team
