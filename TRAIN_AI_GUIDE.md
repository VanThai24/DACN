# HƯỚNG DẪN TRAIN AI VÀ TÍCH HỢP VÀO DESKTOP APP

## 📋 Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Chuẩn Bị Dữ Liệu](#chuẩn-bị-dữ-liệu)
3. [Training Model](#training-model)
4. [Đánh Giá Model](#đánh-giá-model)
5. [Export Model cho Desktop](#export-model-cho-desktop)
6. [Tích Hợp vào Desktop App](#tích-hợp-vào-desktop-app)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Tổng Quan

Quy trình train AI với độ chính xác cao nhất:

```
Chuẩn bị dữ liệu → Train Model → Đánh giá → Export → Tích hợp Desktop
```

### Mục Tiêu
- **Accuracy ≥ 95%** trên validation set
- **Fast inference** cho real-time detection
- **Robust** với lighting, angle variations
- **Small model size** cho desktop deployment

---

## 📁 Chuẩn Bị Dữ Liệu

### 1. Cấu Trúc Thư Mục

```
DACN/AI/face_data/
├── Huy/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── Thai/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── Phong/
│   └── ...
└── ...
```

### 2. Yêu Cầu Dữ Liệu

**Số lượng:**
- **Tối thiểu**: 10-15 ảnh/người
- **Khuyến nghị**: 20-30 ảnh/người
- **Tối ưu**: 50+ ảnh/người

**Chất lượng:**
- ✅ Khuôn mặt rõ ràng, không bị che
- ✅ Đủ ánh sáng
- ✅ Góc chụp đa dạng (thẳng, nghiêng trái/phải)
- ✅ Biểu cảm khác nhau
- ✅ Độ phân giải ≥ 160x160 px
- ❌ Không mờ, không tối
- ❌ Không có nhiều người trong 1 ảnh

### 3. Thu Thập Dữ Liệu

**Cách 1: Chụp từ webcam**
```python
import cv2
import os

name = "Ten_Nguoi"
save_dir = f"face_data/{name}"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0

while count < 30:  # Chụp 30 ảnh
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Press SPACE to capture', frame)
        key = cv2.waitKey(1)
        
        if key == ord(' '):  # Nhấn SPACE để chụp
            cv2.imwrite(f"{save_dir}/{count:03d}.jpg", frame)
            print(f"Captured {count+1}/30")
            count += 1
        elif key == ord('q'):  # Nhấn Q để thoát
            break

cap.release()
cv2.destroyAllWindows()
```

**Cách 2: Từ video**
```python
import cv2
import os

video_path = "video_person.mp4"
name = "Ten_Nguoi"
save_dir = f"face_data/{name}"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
count = 0
frame_skip = 10  # Lấy 1 frame mỗi 10 frames

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if count % frame_skip == 0:
        cv2.imwrite(f"{save_dir}/{count//frame_skip:03d}.jpg", frame)
    
    count += 1

cap.release()
print(f"Extracted {count//frame_skip} images")
```

### 4. Kiểm Tra Dữ Liệu

```python
import os

data_dir = "face_data"
for person in os.listdir(data_dir):
    person_dir = os.path.join(data_dir, person)
    if os.path.isdir(person_dir):
        num_images = len([f for f in os.listdir(person_dir) 
                         if f.endswith(('.jpg', '.jpeg', '.png'))])
        print(f"{person}: {num_images} ảnh")
```

---

## 🚀 Training Model

### 1. Cài Đặt Dependencies

```powershell
cd DACN\AI
pip install tensorflow==2.15.0
pip install numpy opencv-python matplotlib seaborn scikit-learn
pip install pillow
```

### 2. Chạy Training

```powershell
cd DACN\AI
python train_ai_optimized.py
```

### 3. Quá Trình Training

**Phase 1: Train với Base Model Frozen (30 epochs)**
- Base model (MobileNetV2) bị frozen
- Chỉ train Dense layers + Embedding layer
- Learning rate: 0.0001

**Phase 2: Fine-tuning (70 epochs)**
- Unfreeze 50% cuối base model
- Train toàn bộ model
- Learning rate: 0.00001 (thấp hơn 10 lần)

### 4. Callbacks & Optimizations

- **Early Stopping**: Dừng khi val_accuracy không cải thiện sau 15 epochs
- **Learning Rate Reduction**: Giảm LR xuống 50% khi val_loss plateau (5 epochs)
- **Model Checkpoint**: Lưu best model theo val_accuracy
- **TensorBoard**: Log training metrics

### 5. Theo Dõi Training

**Option 1: Console output**
```
Epoch 1/100
45/45 [==============================] - 25s 550ms/step - loss: 2.1234 - accuracy: 0.8567 - val_loss: 1.5432 - val_accuracy: 0.9012
```

**Option 2: TensorBoard**
```powershell
tensorboard --logdir=DACN\AI\logs
```
Mở browser: http://localhost:6006

### 6. Output Files

Sau khi training xong:
```
DACN/AI/
├── faceid_optimized_model.h5        # Model cuối cùng
├── faceid_optimized_best.h5         # Best model (theo val_accuracy)
├── training_history.png              # Biểu đồ training
├── class_mapping.json                # Mapping class index -> name
└── logs/                             # TensorBoard logs
```

---

## 📊 Đánh Giá Model

### 1. Chạy Evaluation

```powershell
cd DACN\AI
python evaluate_model_accuracy.py
```

### 2. Metrics

Script sẽ tính toán:
- **Overall Accuracy**: Độ chính xác tổng thể
- **Precision**: Tỷ lệ dự đoán đúng trong các dự đoán positive
- **Recall**: Tỷ lệ phát hiện đúng trong các mẫu positive thực tế
- **F1-Score**: Trung bình điều hòa của Precision và Recall
- **Confusion Matrix**: Ma trận nhầm lẫn
- **Per-Class Metrics**: Metrics cho từng người

### 3. Đọc Kết Quả

```
================================================================================
KẾT QUẢ TỔNG QUÁT
================================================================================
Overall Accuracy:  96.50%
Weighted Precision: 96.75%
Weighted Recall:    96.50%
Weighted F1-Score:  96.55%
================================================================================
```

**Đánh giá:**
- ✅ **Excellent**: Accuracy ≥ 95%
- ✅ **Good**: Accuracy ≥ 90%
- ⚠️ **Fair**: Accuracy ≥ 85%
- ❌ **Poor**: Accuracy < 85%

### 4. Phân Tích Lỗi

Script sẽ hiển thị:
- Số mẫu bị phân loại sai
- Top 10 lỗi phổ biến nhất
- Confidence distribution (đúng vs sai)

**Ví dụ:**
```
Một số ví dụ phân loại sai:
  1. Sample 45: True='Thai' → Predicted='Huy' (confidence: 78.23%)
  2. Sample 67: True='Phong' → Predicted='Quang' (confidence: 65.44%)
```

### 5. Output Files

```
DACN/AI/
├── confusion_matrix.png           # Ma trận nhầm lẫn
├── per_class_metrics.png          # Metrics từng người
├── confidence_distribution.png    # Phân bố confidence
└── evaluation_results.json        # Kết quả chi tiết (JSON)
```

---

## 📦 Export Model cho Desktop

### 1. Chạy Export Script

```powershell
cd DACN\AI
python export_embedding_model.py
```

### 2. Output Files

```
DACN/AI/
├── faceid_embedding_model.h5      # Embedding model (.h5)
├── faceid_embedding_savedmodel/   # SavedModel format
└── faceid_inference.py            # Helper class
```

### 3. Embedding Model vs Full Model

**Full Model:**
```
Input (160x160x3) → CNN → Embedding (128) → Classification (N classes)
```

**Embedding Model:**
```
Input (160x160x3) → CNN → Embedding (128)
```

Embedding model chỉ output vector 128-dim (L2 normalized), dùng để:
- So sánh similarity giữa 2 faces
- Tìm kiếm face trong database
- Real-time face verification

---

## 🖥️ Tích Hợp vào Desktop App

### 1. Copy Files

```powershell
# Copy model
Copy-Item "DACN\AI\faceid_embedding_model.h5" -Destination "DACN\faceid_desktop\"

# Copy helper
Copy-Item "DACN\AI\faceid_inference.py" -Destination "DACN\faceid_desktop\"

# Copy class mapping (optional)
Copy-Item "DACN\AI\class_mapping.json" -Destination "DACN\faceid_desktop\"
```

### 2. Update Desktop App

**File: `DACN\faceid_desktop\main.py`**

```python
import cv2
import numpy as np
import requests
from faceid_inference import FaceIDEmbedding

class FaceIDApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Load embedding model
        model_path = os.path.join(os.path.dirname(__file__), 
                                  "faceid_embedding_model.h5")
        self.face_model = FaceIDEmbedding(model_path)
        
        # API endpoint
        self.api_url = "http://localhost:5000"
        
    def recognize_face(self, frame):
        """Nhận diện khuôn mặt từ frame"""
        
        # Extract embedding
        embedding = self.face_model.extract_embedding(frame)
        
        # Gửi lên server để match
        response = requests.post(
            f"{self.api_url}/recognize",
            json={
                "embedding": embedding.tolist()
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['name'], result['similarity']
        
        return None, 0.0
    
    def scan_face(self):
        """Quét khuôn mặt từ camera"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Recognize
            name, similarity = self.recognize_face(frame)
            
            if name and similarity > 0.6:  # Threshold
                print(f"Nhận diện: {name} (similarity: {similarity:.2f})")
                # TODO: Cập nhật UI, ghi log, etc.
            
            # Display
            cv2.imshow('Face Scan', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
```

### 3. Sử Dụng Embedding

**So sánh 2 faces:**
```python
# Extract embeddings
emb1 = face_model.extract_embedding(image1)
emb2 = face_model.extract_embedding(image2)

# Cosine similarity
similarity = face_model.cosine_similarity(emb1, emb2)
print(f"Similarity: {similarity:.4f}")

# Check if same person
is_same, score = face_model.is_same_person(emb1, emb2, threshold=0.6)
if is_same:
    print("Same person!")
else:
    print("Different person!")
```

**Tìm kiếm trong database:**
```python
# Load embeddings từ database
database_embeddings = load_embeddings_from_db()

# Extract embedding từ query image
query_embedding = face_model.extract_embedding(query_image)

# Find best match
best_match = None
best_similarity = 0.0

for person_id, db_embedding in database_embeddings.items():
    similarity = face_model.cosine_similarity(query_embedding, db_embedding)
    if similarity > best_similarity:
        best_similarity = similarity
        best_match = person_id

if best_similarity > 0.6:  # Threshold
    print(f"Matched: {best_match} (similarity: {best_similarity:.2f})")
else:
    print("No match found")
```

### 4. Threshold Tuning

**Recommended thresholds:**
- **Strict** (High security): 0.7 - 0.8
- **Balanced**: 0.6 - 0.7
- **Loose** (High recall): 0.5 - 0.6

Tune threshold dựa trên:
- False Positive Rate (FPR): Người lạ bị nhận diện nhầm
- False Negative Rate (FNR): Người đúng bị từ chối

---

## 🔧 Troubleshooting

### 1. Training Issues

**Problem: Loss không giảm**
```
Solutions:
- Giảm learning rate
- Tăng batch size
- Kiểm tra dữ liệu (có bị lỗi không?)
- Thử architecture khác
```

**Problem: Overfitting (val_loss tăng)**
```
Solutions:
- Tăng dropout rate
- Thêm data augmentation
- Thêm L2 regularization
- Thu thập thêm data
```

**Problem: Underfitting (accuracy thấp)**
```
Solutions:
- Tăng model capacity (thêm layers)
- Train lâu hơn
- Giảm regularization
- Kiểm tra data quality
```

### 2. Data Issues

**Problem: Không đủ dữ liệu**
```
Solutions:
- Data augmentation mạnh hơn
- Thu thập thêm từ video
- Synthesize data (GAN, morphing)
```

**Problem: Imbalanced classes**
```
Solutions:
- Oversample minority classes
- Undersample majority classes
- Class weights trong loss function
- SMOTE (Synthetic Minority Over-sampling)
```

### 3. Inference Issues

**Problem: Inference chậm**
```
Solutions:
- Quantization (TFLite, ONNX)
- Model pruning
- Use smaller model
- Batch processing
- GPU acceleration
```

**Problem: Accuracy thấp trên real data**
```
Solutions:
- Retrain với real data
- Fine-tune với real data
- Adjust threshold
- Improve preprocessing
```

### 4. Integration Issues

**Problem: Model không load được**
```python
# Thêm custom_objects khi load
model = tf.keras.models.load_model(
    model_path,
    custom_objects={'l2_normalize_func': l2_normalize_func}
)
```

**Problem: Embedding không consistent**
```python
# Đảm bảo preprocessing giống training
- Resize đúng size (160x160)
- BGR → RGB conversion
- Normalize [0, 255] → [0, 1]
- Đúng thứ tự channels (RGB)
```

---

## 📈 Best Practices

### 1. Data Collection
- ✅ Collect diverse data (lighting, angles, expressions)
- ✅ Use high-quality images
- ✅ Balance classes (same number of images per person)
- ✅ Validate data quality before training

### 2. Training
- ✅ Use transfer learning (faster, better accuracy)
- ✅ Use data augmentation
- ✅ Monitor validation metrics
- ✅ Use callbacks (early stopping, LR reduction)
- ✅ Save best model, not final model

### 3. Evaluation
- ✅ Test on separate validation set
- ✅ Check confusion matrix
- ✅ Analyze misclassified samples
- ✅ Test with real-world data

### 4. Deployment
- ✅ Use embedding model (faster)
- ✅ Optimize inference (TFLite, ONNX)
- ✅ Set appropriate threshold
- ✅ Monitor performance in production
- ✅ Collect feedback for retraining

---

## 📚 References

### Papers
- FaceNet: https://arxiv.org/abs/1503.03832
- MobileNetV2: https://arxiv.org/abs/1801.04381
- ArcFace: https://arxiv.org/abs/1801.07698

### Tutorials
- TensorFlow Face Recognition: https://www.tensorflow.org/tutorials
- Keras Transfer Learning: https://keras.io/guides/transfer_learning/

### Tools
- TensorBoard: https://www.tensorflow.org/tensorboard
- scikit-learn: https://scikit-learn.org/

---

## 🎯 Quick Start

### Quy trình nhanh (5 bước):

```powershell
# 1. Chuẩn bị dữ liệu
# Tạo folder face_data với ảnh các người

# 2. Train model
cd DACN\AI
python train_ai_optimized.py

# 3. Đánh giá
python evaluate_model_accuracy.py

# 4. Export embedding model
python export_embedding_model.py

# 5. Copy vào desktop app
Copy-Item "faceid_embedding_model.h5" -Destination "..\faceid_desktop\"
Copy-Item "faceid_inference.py" -Destination "..\faceid_desktop\"
```

---

## 📞 Support

Nếu gặp vấn đề, check:
1. Console output (error messages)
2. TensorBoard logs
3. Evaluation results
4. Data quality

---

**Happy Training! 🚀**
