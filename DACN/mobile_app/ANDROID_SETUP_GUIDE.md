# 📱 HƯỚNG DẪN KẾT NỐI ANDROID STUDIO VỚI MOBILE APP

## 🎯 CÁC CÁCH XEM APP REACT NATIVE/EXPO

### **CÁCH 1: SỬ DỤNG EXPO GO (KHUYẾN NGHỊ - DỄ NHẤT)** ⭐

#### Bước 1: Cài đặt Expo Go trên điện thoại
- **Android:** [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
- **iOS:** [App Store](https://apps.apple.com/app/expo-go/id982107779)

#### Bước 2: Chạy ứng dụng
```bash
cd D:\DACN\DACN\mobile_app
npm install
npx expo start
```

#### Bước 3: Quét QR Code
- Mở Expo Go app
- Quét QR code hiển thị trong terminal
- App sẽ tự động load và hot reload khi bạn sửa code

**Ưu điểm:**
✅ Không cần Android Studio  
✅ Hot reload cực nhanh  
✅ Test trên thiết bị thật  
✅ Không cần build APK  

**Nhược điểm:**
❌ Cần cùng mạng WiFi với máy tính  
❌ Không test được native modules đặc biệt  

---

### **CÁCH 2: ANDROID EMULATOR (ANDROID STUDIO)** 🖥️

#### A. Cài đặt Android Studio

1. **Download Android Studio:**
   - [https://developer.android.com/studio](https://developer.android.com/studio)

2. **Cài đặt Android SDK:**
   - Mở Android Studio
   - `Tools` → `SDK Manager`
   - Chọn **Android 13.0 (API 33)** hoặc mới hơn
   - Install packages

3. **Cài đặt Android Emulator:**
   - `Tools` → `Device Manager`
   - `Create Device` → Chọn `Pixel 5` hoặc `Pixel 7`
   - Chọn System Image: **Android 13 (API 33)**
   - Finish và khởi động emulator

#### B. Cấu hình Environment Variables

**Windows:**
```powershell
# Thêm vào System Environment Variables
ANDROID_HOME=C:\Users\YourUsername\AppData\Local\Android\Sdk

# Thêm vào PATH:
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\emulator
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
```

**Kiểm tra:**
```bash
adb --version
# Nếu thấy version → Thành công!
```

#### C. Chạy App trên Emulator

```bash
# Terminal 1: Khởi động emulator (nếu chưa chạy)
emulator -list-avds  # Xem danh sách
emulator -avd Pixel_5_API_33  # Thay tên emulator của bạn

# Terminal 2: Chạy app
cd D:\DACN\DACN\mobile_app
npx expo start --android
# Hoặc nhấn 'a' trong terminal Expo
```

**Hot Reload:**
- **Shake device** (trong emulator: `Ctrl + M` hoặc `Cmd + M`)
- Chọn `Enable Hot Reloading`
- Code thay đổi → App tự động reload

---

### **CÁCH 3: BUILD APK VÀ INSTALL** 📦

#### A. Build APK với Expo

```bash
cd D:\DACN\DACN\mobile_app

# Build APK
eas build --platform android --profile preview

# Hoặc build local (không cần Expo account)
npx expo export --platform android
```

#### B. Build với React Native CLI (không dùng Expo)

```bash
# Nếu eject khỏi Expo
cd android
./gradlew assembleDebug

# APK sẽ ở: android/app/build/outputs/apk/debug/app-debug.apk
```

#### C. Install APK lên Emulator

```bash
adb install app-debug.apk

# Hoặc kéo thả file APK vào emulator
```

---

## 🔧 TROUBLESHOOTING

### ❌ Lỗi: "Unable to connect to Metro"

**Giải pháp:**
```bash
# 1. Clear cache
npx expo start --clear

# 2. Reset Metro bundler
npx react-native start --reset-cache

# 3. Kiểm tra firewall
# Cho phép port 8081 và 19000
```

### ❌ Lỗi: "adb not found"

**Giải pháp:**
```bash
# Kiểm tra PATH
echo %ANDROID_HOME%

# Thêm platform-tools vào PATH
# Restart terminal sau khi thêm
```

### ❌ Emulator chạy chậm

**Giải pháp:**
1. Enable **Hardware Acceleration (HAXM)**:
   - SDK Manager → SDK Tools → Intel HAXM
   
2. Tăng RAM cho emulator:
   - Device Manager → Edit Device → Advanced Settings
   - RAM: 2048 MB → 4096 MB

3. Dùng thiết bị thật thay vì emulator

### ❌ Không kết nối được với backend

**Kiểm tra config.js:**
```javascript
// ❌ SAI - localhost không work trên emulator
export const API_BASE_URL = "http://localhost:8000";

// ✅ ĐÚNG - Dùng IP máy hoặc 10.0.2.2
export const API_BASE_URL = "http://10.0.2.2:8000";  // Emulator
// hoặc
export const API_BASE_URL = "http://192.168.1.100:8000";  // Thiết bị thật
```

**Lấy IP máy:**
```bash
# Windows
ipconfig
# Tìm IPv4 Address

# Linux/Mac
ifconfig
```

---

## 📱 SO SÁNH CÁC PHƯƠNG PHÁP

| Phương pháp | Tốc độ | Dễ setup | Hot reload | Native modules |
|-------------|--------|----------|------------|----------------|
| **Expo Go** | ⚡⚡⚡ | ✅✅✅ | ✅✅✅ | ⚠️ Hạn chế |
| **Emulator** | ⚡⚡ | ✅✅ | ✅✅ | ✅ Đầy đủ |
| **Physical Device** | ⚡⚡⚡ | ✅✅✅ | ✅✅✅ | ✅ Đầy đủ |
| **APK Build** | ⚡ | ✅ | ❌ Không | ✅ Đầy đủ |

---

## 🎯 KHUYẾN NGHỊ CHO PROJECT NÀY

### **Development (Đang code):**
```bash
# Dùng Expo Go - Nhanh nhất!
cd D:\DACN\DACN\mobile_app
npx expo start

# Quét QR code bằng Expo Go app
```

### **Testing (Kiểm tra tính năng):**
```bash
# Dùng Android Emulator
npx expo start --android

# Hoặc physical device qua USB
npx expo start --android --device
```

### **Production (Phát hành):**
```bash
# Build APK
eas build --platform android --profile production
```

---

## 🔗 LIÊN KẾT HỮU ÍCH

- **Expo Documentation:** https://docs.expo.dev
- **Android Studio Setup:** https://developer.android.com/studio/install
- **React Native Debugging:** https://reactnative.dev/docs/debugging
- **ADB Commands:** https://developer.android.com/studio/command-line/adb

---

## 💡 TIPS & TRICKS

### 1. **Debug Menu trong App**
```
# Emulator
Ctrl + M (Windows)
Cmd + M (Mac)

# Physical Device
Shake device
```

### 2. **View Logs**
```bash
# Expo logs
npx expo start

# React Native logs
npx react-native log-android

# ADB logs
adb logcat | grep "ReactNative"
```

### 3. **Hot Reload không hoạt động**
```bash
# Enable trong debug menu
Ctrl + M → Enable Fast Refresh

# Hoặc dùng Live Reload
Ctrl + M → Enable Live Reload
```

### 4. **Clear Cache**
```bash
# Clear Expo cache
npx expo start --clear

# Clear npm cache
npm cache clean --force

# Clear Metro bundler
rm -rf node_modules
npm install
```

### 5. **Kết nối qua USB (Physical Device)**
```bash
# Enable USB Debugging trên điện thoại
# Settings → Developer Options → USB Debugging

# Kiểm tra device
adb devices

# Chạy app
npx expo start --android
```

---

## 📞 HỖ TRỢ

**Nếu gặp vấn đề:**
1. Đọc lỗi trong terminal
2. Kiểm tra `package.json` và dependencies
3. Google lỗi cụ thể
4. Kiểm tra Expo/React Native GitHub Issues

**Common Issues:**
- Port bị chiếm → Đổi port: `npx expo start --port 8082`
- Metro bundler crash → `npx expo start --clear`
- Module not found → `npm install` lại
- Backend không connect → Kiểm tra IP trong `config.js`

---

**Tóm lại:** Dùng **Expo Go** cho development hàng ngày, **Android Emulator** khi cần test kỹ! 🚀
