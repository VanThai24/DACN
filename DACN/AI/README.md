# 🤖 AI Module - Face Recognition System

## 📋 Tổng Quan
Module AI sử dụng thuật toán **Face Recognition (dlib) + SVM** để nhận diện khuôn mặt và điểm danh tự động.

### 🎯 Kết Quả
- **Train Accuracy**: 100%
- **Test Accuracy**: 100%
- **Confidence**: 58.61% ± 19.86%
- **Best Hyperparameters**: C=10, gamma='scale', kernel='rbf'
- **Số lượng classes**: 5 nhân viên

---

## 📂 Cấu Trúc Files

### 🔥 Core Files
```
app.py                              # Flask API Server
train_best_model.py                 # Model Training Script
update_embeddings_best_model.py     # Update Database Embeddings
faceid_best_model.pkl              # Trained SVM Model
faceid_best_model_metadata.pkl     # Model Metadata
```

### 🛠️ Utility Scripts
```
add_new_employee.py                 # Add New Employee (Auto)
add_new_employee.bat               # Windows Batch Script
capture_training_data.py           # Capture Training Images
augment_data.py                    # Data Augmentation
auto_augment.py                    # Auto Augment All Employees
check_data.py                      # Check Training Data Status
create_dummy_data.py               # Generate Dummy Employees
```

### 📁 Data Folders
```
face_data/                         # Training Images
  ├── Huy/                        # Employee 1 (40 images)
  ├── Phong/                      # Employee 2 (40 images)
  ├── Phát/                       # Employee 3 (40 images)
  ├── Quang/                      # Employee 4 (40 images)
  ├── Thai/                       # Employee 5 (40 images)
  └── Thiện/                      # Employee 6 (40 images)
```

---

## 🚀 Quick Start

### 1️⃣ Chạy Flask API Server
```bash
python app.py
```
Server chạy tại: `http://localhost:5000`

**Endpoints:**
- `POST /recognize` - Nhận diện khuôn mặt và điểm danh
- `GET /health` - Health check

### 2️⃣ Kiểm Tra Dữ Liệu
```bash
python check_data.py
```
Hiển thị số lượng ảnh của mỗi nhân viên.

### 3️⃣ Thêm Nhân Viên Mới
```bash
.\add_new_employee.bat
# hoặc
python add_new_employee.py
```

**Quy trình:**
1. Chụp 15-20 ảnh (5 góc độ)
2. Tăng cường lên 40 ảnh
3. Train lại model
4. Cập nhật embeddings

⏱️ **Thời gian**: ~10 phút

---

## 🧠 Training Pipeline

### Step 1: Thu Thập Dữ Liệu
```bash
python capture_training_data.py
```
- Chụp 50 ảnh với 5 góc độ khác nhau
- Tự động crop và resize
- Lưu vào `face_data/<tên>/`

### Step 2: Tăng Cường Dữ Liệu (Nếu <40 ảnh)
```bash
python augment_data.py
```
**Kỹ thuật augmentation:**
- Rotation (±20°)
- Horizontal flip
- Brightness adjustment (0.7-1.3)
- Gaussian blur
- Gaussian noise
- Contrast adjustment

### Step 3: Train Model
```bash
python train_best_model.py
```
**GridSearchCV params:**
```python
param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
    'kernel': ['rbf', 'linear']
}
```

**Output:**
- `faceid_best_model.pkl` - Trained model
- `faceid_best_model_metadata.pkl` - Metadata

### Step 4: Cập Nhật Database
```bash
python update_embeddings_best_model.py
```
Lưu 128-dim face embeddings vào MySQL `employees` table.

---

## 📊 Model Performance

### Current Stats
```
Classes: 5 employees
Total samples: 24 embeddings
Train accuracy: 100%
Test accuracy: 100%
Average confidence: 58.61% ± 19.86%
```

### Confusion Matrix
```
Perfect diagonal (100% accuracy)
```

### Best Hyperparameters
```python
{
    'C': 10,
    'gamma': 'scale',
    'kernel': 'rbf'
}
```

---

## 🔧 Configuration

### Database Connection
```python
# db.py
host = "localhost"
user = "root"
password = "12345"
database = "attendance_db"
```

### Face Recognition Settings
```python
# train_best_model.py
model = 'large'  # dlib model (large = more accurate)
num_jitters = 1  # Number of times to re-sample
```

### Thresholds
```python
# app.py
confidence_threshold = 0.4  # Minimum confidence
distance_threshold = 0.6    # Maximum face distance
```

---

## 📖 API Documentation

### POST /recognize
**Request:**
```json
{
  "image": "base64_encoded_image_string"
}
```

**Response (Success):**
```json
{
  "success": true,
  "employee_id": 71,
  "employee_name": "Nguyễn Văn Huy",
  "confidence": 0.7854,
  "shift_id": 1,
  "shift_name": "Ca Sáng",
  "message": "Điểm danh thành công!"
}
```

**Response (Already Checked In):**
```json
{
  "success": false,
  "error": "Bạn đã điểm danh ca này rồi!",
  "employee_name": "Nguyễn Văn Huy",
  "existing_record": {
    "timestamp": "2025-11-15 08:30:00"
  }
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "error": "Không tìm thấy khuôn mặt trong database"
}
```

---

## 🛠️ Troubleshooting

### ❌ Không Nhận Diện Được
**Nguyên nhân:**
- Ảnh quá tối/quá sáng
- Góc chụp không phù hợp
- Khuôn mặt bị che khuất
- Chưa có trong database

**Giải pháp:**
1. Kiểm tra ánh sáng
2. Chụp thẳng vào camera
3. Train lại với nhiều ảnh hơn

### ❌ Confidence Thấp (<40%)
**Nguyên nhân:**
- Dữ liệu training không đủ đa dạng
- Lighting khác biệt giữa train và test
- Góc chụp khác nhau

**Giải pháp:**
1. Chụp thêm ảnh với nhiều góc độ
2. Chụp ở nhiều điều kiện ánh sáng
3. Sử dụng augmentation
4. Tăng `num_jitters` trong training

### ❌ Lỗi Database
**Giải pháp:**
```bash
# Kiểm tra MySQL đang chạy
mysql -u root -p12345 attendance_db
```

---

## 📚 Thuật Toán

### Face Recognition
1. **Face Detection**: HOG-based detector
2. **Face Alignment**: 68 facial landmarks
3. **Feature Extraction**: 128-dim embedding (ResNet)
4. **Classification**: SVM with RBF kernel

### Training Process
```
Input: face_data/ folder
↓
Load all images
↓
Extract 128-dim embeddings (dlib)
↓
GridSearchCV for best SVM params
↓
Train SVM classifier
↓
Save model + metadata
```

### Prediction Process
```
Input: Camera image
↓
Detect faces (HOG)
↓
Extract embedding
↓
SVM predict
↓
Check confidence
↓
Query database
↓
Check duplicate attendance
↓
Insert record
```

---

## 🎯 Best Practices

### Training Data
- ✅ Minimum 40 ảnh/người
- ✅ Nhiều góc độ (straight, left, right, up, down)
- ✅ Nhiều điều kiện ánh sáng
- ✅ Nhiều biểu cảm khác nhau
- ❌ Tránh ảnh mờ, tối
- ❌ Tránh ảnh bị che khuất

### Model Tuning
- 🔧 Tăng `C` nếu underfitting
- 🔧 Giảm `C` nếu overfitting
- 🔧 Thử `gamma='auto'` nếu data lớn
- 🔧 Thử `kernel='linear'` nếu data ít

### Production Tips
- 💡 Cache face embeddings để tăng tốc
- 💡 Resize ảnh xuống 800x600 trước khi xử lý
- 💡 Sử dụng GPU nếu có (dlib CUDA)
- 💡 Rate limiting cho API

---

## 📦 Dependencies

```
face_recognition>=1.3.0
dlib>=19.24.0
opencv-python>=4.8.0
scikit-learn>=1.3.0
numpy>=1.24.0
Pillow>=10.0.0
Flask>=2.3.0
flask-cors>=4.0.0
mysql-connector-python>=8.1.0
joblib>=1.3.0
```

Install:
```bash
pip install -r requirements.txt
```

---

## 🚀 Performance Optimization

### Speed
- ⚡ Face detection: ~50ms
- ⚡ Feature extraction: ~100ms
- ⚡ SVM prediction: <1ms
- ⚡ **Total**: ~150-200ms

### Memory
- 💾 Model size: ~500KB
- 💾 Per embedding: 128 floats = 512 bytes
- 💾 100 employees = ~50KB

---

## 📝 Notes

### ⚠️ Lưu Ý
- Model cần **retrain** khi thêm nhân viên mới
- Embeddings cần **update** sau mỗi lần train
- Backup model file trước khi train lại
- Test kỹ sau khi train mới

### 🎓 Thesis Tips
- Demo với 5-10 người là đủ
- Focus vào accuracy, không cần scale lớn
- Prepare kịch bản demo trước
- Có backup plan nếu camera lỗi

---

**📅 Last Updated**: November 2025  
**🎯 Purpose**: Thesis Project Only
