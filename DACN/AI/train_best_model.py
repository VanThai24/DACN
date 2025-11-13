"""
Train AI với Dữ Liệu Gốc - Không Augmentation
Sử dụng Face Recognition + SVM với config tối ưu
"""

import os
import numpy as np
import face_recognition
import cv2
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from glob import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'face_data')
MODEL_OUTPUT = os.path.join(BASE_DIR, 'faceid_best_model.pkl')

print("=" * 80)
print("TRAINING AI VỚI DỮ LIỆU GỐC - TỐI ƯU HÓA")
print("=" * 80)
print(f"Data folder: {DATA_DIR}")
print(f"Model output: {MODEL_OUTPUT}")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATA VỚI KỸ THUẬT RESIZE
# ============================================================================

print("\n[1/6] Loading images với preprocessing...")

if not os.path.exists(DATA_DIR):
    print(f"❌ Folder không tồn tại: {DATA_DIR}")
    exit(1)

embeddings = []
labels = []
person_names = sorted(os.listdir(DATA_DIR))
person_names = [p for p in person_names if os.path.isdir(os.path.join(DATA_DIR, p))]

print(f"✅ Found {len(person_names)} persons")

for person_name in person_names:
    person_dir = os.path.join(DATA_DIR, person_name)
    
    image_files = glob(os.path.join(person_dir, '*.*'))
    image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"\n  Processing {person_name}...")
    
    success_count = 0
    fail_count = 0
    
    for img_path in image_files:
        try:
            # Load với Unicode support
            with open(img_path, 'rb') as f:
                img_array = np.frombuffer(f.read(), dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if image is None:
                fail_count += 1
                continue
            
            # Resize to optimal size (face_recognition works better with larger images)
            h, w = image.shape[:2]
            if w < 300:
                scale = 300 / w
                image = cv2.resize(image, (int(w * scale), int(h * scale)))
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get face encodings với model='large' cho accuracy cao hơn
            face_encodings = face_recognition.face_encodings(image, model='large')
            
            if len(face_encodings) == 0:
                fail_count += 1
                continue
            
            # Take first face
            embedding = face_encodings[0]
            
            embeddings.append(embedding)
            labels.append(person_name)
            success_count += 1
            
        except Exception as e:
            fail_count += 1
            continue
    
    print(f"    ✅ Success: {success_count}, ❌ Failed: {fail_count}")

embeddings = np.array(embeddings)
labels = np.array(labels)

print(f"\n✅ Total embeddings: {len(embeddings)}")
print(f"✅ Unique classes: {np.unique(labels)}")

# Remove classes with < 2 samples
unique_classes, class_counts = np.unique(labels, return_counts=True)
valid_classes = unique_classes[class_counts >= 2]

if len(valid_classes) < len(unique_classes):
    print(f"\n⚠️  Removing classes with <2 samples: {unique_classes[class_counts < 2]}")
    mask = np.isin(labels, valid_classes)
    embeddings = embeddings[mask]
    labels = labels[mask]
    print(f"✅ After filter: {len(embeddings)} samples, {len(valid_classes)} classes")

# ============================================================================
# STEP 2: TRAIN/TEST SPLIT
# ============================================================================

print("\n[2/6] Splitting train/test...")

X_train, X_test, y_train, y_test = train_test_split(
    embeddings, labels, 
    test_size=0.25,  # 25% for test
    random_state=42,
    stratify=labels
)

print(f"✅ Train samples: {len(X_train)}")
print(f"✅ Test samples: {len(X_test)}")

unique_train, counts_train = np.unique(y_train, return_counts=True)
print("\n📊 Train distribution:")
for cls, cnt in zip(unique_train, counts_train):
    print(f"  {cls:<30}: {cnt:>2} samples")

# ============================================================================
# STEP 3: HYPERPARAMETER TUNING với GridSearchCV
# ============================================================================

print("\n[3/6] Hyperparameter tuning...")

param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
    'kernel': ['rbf', 'linear']
}

print(f"⏳ Testing {len(param_grid['C']) * len(param_grid['gamma']) * len(param_grid['kernel'])} combinations...")

svc = SVC(probability=True, random_state=42)
grid_search = GridSearchCV(svc, param_grid, cv=3, n_jobs=-1, verbose=1, scoring='accuracy')
grid_search.fit(X_train, y_train)

print(f"\n✅ Best parameters: {grid_search.best_params_}")
print(f"✅ Best CV score: {grid_search.best_score_*100:.2f}%")

clf = grid_search.best_estimator_

# ============================================================================
# STEP 4: EVALUATE
# ============================================================================

print("\n[4/6] Evaluating model...")

# Train accuracy
y_train_pred = clf.predict(X_train)
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"✅ Train Accuracy: {train_accuracy*100:.2f}%")

# Test accuracy
y_test_pred = clf.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"✅ Test Accuracy: {test_accuracy*100:.2f}%")

# Confidence scores
y_test_proba = clf.predict_proba(X_test)
y_test_confidence = np.max(y_test_proba, axis=1)

correct_mask = y_test_pred == y_test
correct_confidence = y_test_confidence[correct_mask]
incorrect_confidence = y_test_confidence[~correct_mask]

print(f"\n📊 Confidence Analysis:")
print(f"  All: {y_test_confidence.mean()*100:.2f}% ± {y_test_confidence.std()*100:.2f}%")
if len(correct_confidence) > 0:
    print(f"  Correct: {correct_confidence.mean()*100:.2f}% ± {correct_confidence.std()*100:.2f}%")
if len(incorrect_confidence) > 0:
    print(f"  Incorrect: {incorrect_confidence.mean()*100:.2f}% ± {incorrect_confidence.std()*100:.2f}%")

# Confusion matrix
print("\n📊 Confusion Matrix:")
cm = confusion_matrix(y_test, y_test_pred, labels=clf.classes_)
print(cm)

# Per-class accuracy
print("\n📊 Per-class Accuracy:")
for i, cls in enumerate(clf.classes_):
    cls_mask = y_test == cls
    if np.sum(cls_mask) > 0:
        cls_acc = accuracy_score(y_test[cls_mask], y_test_pred[cls_mask])
        print(f"  {cls:<30}: {cls_acc*100:.2f}% ({np.sum(cls_mask)} samples)")

# Classification report
print("\n📊 Classification Report:")
print(classification_report(y_test, y_test_pred, target_names=clf.classes_, zero_division=0))

# ============================================================================
# STEP 5: SAVE MODEL
# ============================================================================

print("\n[5/6] Saving model...")

joblib.dump(clf, MODEL_OUTPUT)
print(f"✅ Model saved: {MODEL_OUTPUT}")

# Save metadata
metadata = {
    'embeddings': embeddings,
    'labels': labels,
    'classes': clf.classes_,
    'best_params': grid_search.best_params_,
    'train_accuracy': train_accuracy,
    'test_accuracy': test_accuracy,
    'avg_confidence': y_test_confidence.mean()
}

metadata_file = os.path.join(BASE_DIR, 'faceid_best_model_metadata.pkl')
joblib.dump(metadata, metadata_file)
print(f"✅ Metadata saved: {metadata_file}")

# ============================================================================
# STEP 6: RECOMMENDATIONS
# ============================================================================

print("\n[6/6] Analysis & Recommendations...")

print("\n" + "=" * 80)
print("🎉 TRAINING HOÀN TẤT!")
print("=" * 80)
print(f"✅ Model: {MODEL_OUTPUT}")
print(f"✅ Classes: {len(clf.classes_)}")
print(f"✅ Train Accuracy: {train_accuracy*100:.2f}%")
print(f"✅ Test Accuracy: {test_accuracy*100:.2f}%")
print(f"✅ Avg Confidence: {y_test_confidence.mean()*100:.2f}%")
print(f"✅ Best params: {grid_search.best_params_}")

if test_accuracy >= 0.85:
    print("\n🎯 Model ĐẠT YÊU CẦU! (≥85%)")
    print("\nBước tiếp theo:")
    print("  1. python test_best_model_webcam.py  # Test với webcam")
    print("  2. Tích hợp vào desktop app")
elif test_accuracy >= 0.70:
    print(f"\n⚠️  Model CHẤP NHẬN ĐƯỢC (70-85%): {test_accuracy*100:.2f}%")
    print("\nCó thể dùng nhưng nên cải thiện:")
    print("  - Thu thập thêm 10-20 ảnh/người với góc độ đa dạng")
    print("  - Đảm bảo ánh sáng tốt khi chụp")
    print("  - Test với python test_best_model_webcam.py")
else:
    print(f"\n❌ Model CHƯA ĐẠT (<70%): {test_accuracy*100:.2f}%")
    print("\nNguyên nhân:")
    print(f"  - Quá ít dữ liệu training: {len(X_train)} samples")
    print(f"  - Classes có ít ảnh: {dict(zip(unique_train, counts_train))}")
    print("\nGiải pháp:")
    print("  - Thu thập 30-50 ảnh/người")
    print("  - Chạy: python create_synthetic_dataset.py")

print("=" * 80)
