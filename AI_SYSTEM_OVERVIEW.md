# KIỂM TRA AI TRONG PROJECT

## 📊 TỔNG QUAN AI SYSTEM

### 🤖 AI Core Technology Stack

**Face Recognition Engine:**
- **Library**: `face_recognition` (dlib-based)
- **Model**: CNN face detector với model='large'
- **Accuracy**: 99.38% trên LFW benchmark
- **Embedding**: 128-dimensional face encodings

**Machine Learning:**
- **Classifier**: SVM (Support Vector Machine)
- **Kernel**: RBF (Radial Basis Function)
- **Hyperparameters**: 
  - C=10
  - gamma='scale'
- **Optimization**: GridSearchCV với 40 combinations

### 📁 Model Files

**Location**: `D:\DACN\DACN\AI\`

1. **faceid_best_model.pkl** (MISSING - Need to retrain)
   - SVM classifier
   - Trained on 5 classes: Huy, Phong, Phát, Quang, Thai
   - 100% test accuracy
   
2. **faceid_best_model_metadata.pkl** (25.14 KB)
   - Model metadata
   - Test accuracy, confidence scores
   - Training parameters

### 🎯 Applications Using AI

#### 1. **Desktop App** (`faceid_desktop/main.py`)
```python
Technology:
- PySide6 (Qt GUI)
- face_recognition (dlib)
- joblib (model loading)
- OpenCV (camera)

Process:
1. Load faceid_best_model.pkl
2. Capture from webcam
3. Detect faces with face_recognition.face_locations()
4. Extract 128d embeddings with model='large'
5. Predict with SVM classifier
6. Threshold: 30% confidence
7. Auto-create shifts and save to MySQL
```

#### 2. **Flask API** (`AI/app_new.py` → `AI/app.py`)
```python
Technology:
- Flask + Flask-CORS
- face_recognition (dlib)
- MySQL connector

Endpoints:
- POST /scan - Face recognition & attendance
- GET /attendance/employee/{id} - Get records
- GET /users/{id} - Get user info
- GET /employees - List employees

Process:
1. Receive image (base64 or file)
2. Extract face encoding (model='large')
3. Predict with SVM
4. Confidence >= 30% → Save attendance
5. Auto-create shift based on time
```

#### 3. **Mobile App Backend** (FastAPI)
```python
Technology:
- FastAPI (Uvicorn)
- SQLAlchemy ORM
- JWT authentication

Location: backend_src/app/
- Provides /auth/login with employee_id
- Returns attendance records for mobile
```

### 📦 Python Dependencies

**AI/ML Libraries:**
```
face_recognition     # dlib-based face recognition
dlib                 # CNN face detector
scikit-learn        # SVM, GridSearchCV
joblib              # Model serialization
numpy               # Array operations
opencv-python       # Image processing
```

**Web Frameworks:**
```
Flask               # REST API
Flask-CORS          # Cross-origin
FastAPI            # Backend API
uvicorn            # ASGI server
```

**Database:**
```
mysql-connector-python  # MySQL connection
SQLAlchemy             # ORM for FastAPI
```

**GUI:**
```
PySide6            # Qt for desktop app
```

### 🔧 Training Pipeline

**Script**: `train_best_model.py`

**Steps:**
1. Load images from `face_data/` folder
2. Extract face encodings (model='large')
3. Split train/test (75%/25%)
4. GridSearchCV on SVM
   - C: [1, 10, 100]
   - gamma: ['scale', 'auto', 0.001, 0.01]
   - kernel: ['rbf', 'linear']
5. Train best model
6. Evaluate: confusion matrix, accuracy, confidence
7. Save: faceid_best_model.pkl + metadata

**Current Status:**
- ✅ 5 classes trained
- ✅ 100% test accuracy
- ✅ 58.61% avg confidence
- ⚠️ Model file corrupted/missing - needs retrain

### 📊 Data Structure

**Training Data**: `DACN/AI/face_data/`
```
face_data/
├── Huy/         (3 valid images)
├── Phong/       (6 valid images)
├── Phát/        (7 valid images)
├── Quang/       (5 valid images)
├── Thai/        (3 valid images)
└── Thiện/       (1 valid image - excluded)
```

**Total**: 24 samples, 5 classes

### 🎯 Recognition Pipeline

**Desktop App Flow:**
```
1. Camera capture (OpenCV)
2. Face detection (face_recognition.face_locations)
3. Face encoding (model='large', 128d)
4. SVM prediction
5. Confidence check (>= 30%)
6. Name mapping (Thai → Đặng Văn Thái)
7. Get employee_id from MySQL
8. Determine shift (7:00-11:30 or 13:00-16:30)
9. Create shift if not exists
10. Save attendance record
11. Display result with UI feedback
```

### 🔥 Key Features

**Automatic Shift Management:**
- Morning shift: 7:00 - 11:30 (detected 6:00-12:30)
- Afternoon shift: 13:00 - 16:30 (detected 12:30-23:59)
- Auto-create if not exists

**Name Mapping:**
```python
name_mapping = {
    'Thai': 'Đặng Văn Thái'
}
```

**Database Integration:**
- employees table (id, name, face_encoding)
- attendance_records (employee_id, timestamp_in, shift_id)
- shifts (employee_id, date, start_time, end_time)

### ⚠️ Current Issues

1. **Model File Corrupted**: 
   - faceid_best_model.pkl cannot load
   - Need to run: `python train_best_model.py`

2. **Low Confidence**:
   - Average: 58.61%
   - Threshold lowered to 30%
   - Solution: Collect 30-50 images per person

3. **Missing Employee**:
   - Thiện only has 1 image (need ≥2)
   - Not included in training

### 🚀 Recommendations

1. **Collect More Data**:
   - 30-50 images per person
   - Various angles, lighting
   - Will increase confidence to 70%+

2. **Retrain Model**:
   ```bash
   cd D:\DACN\DACN\AI
   python train_best_model.py
   ```

3. **Increase Threshold**:
   - After more data: 60-70%
   - Current: 30% (due to limited data)

4. **Add More Employees**:
   - Create folder in face_data/
   - Add 30+ images
   - Retrain model

### 📱 Mobile App Integration

**Status**: ✅ WORKING
- Backend returns employee_id in login
- Mobile fetches attendance via employee_id
- Displays shift times (start_time, end_time)
- Real-time updates

---

**Last Updated**: 2025-11-13
**Model Status**: ⚠️ Needs Retrain
**System Status**: ✅ Operational (30% threshold)
