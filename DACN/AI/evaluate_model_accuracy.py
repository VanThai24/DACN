"""
Evaluate Model Accuracy - Đánh giá chi tiết độ chính xác của model
Tính toán Accuracy, Precision, Recall, F1-Score và Confusion Matrix
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_recall_fscore_support
import json

# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'face_data')

# Chọn model để evaluate (bạn có thể thay đổi đường dẫn này)
MODEL_PATH = os.path.join(BASE_DIR, 'faceid_optimized_best.h5')
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, 'faceid_model_tf_best.h5')
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, 'faceid_model_tf.h5')

IMG_SIZE = (160, 160)
BATCH_SIZE = 16

print("=" * 80)
print("ĐÁNH GIÁ ĐỘ CHÍNH XÁC MODEL FACEID")
print("=" * 80)
print(f"Model: {MODEL_PATH}")
print(f"Data: {DATA_DIR}")
print("=" * 80)

# ============================================================================
# LOAD MODEL
# ============================================================================

print("\n[1/6] Loading model...")
try:
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={'l2_normalize_func': l2_normalize_func}
    )
    print(f"✓ Model loaded successfully")
    print(f"✓ Input shape: {model.input_shape}")
    print(f"✓ Output shape: {model.output_shape}")
except Exception as e:
    print(f"✗ Lỗi khi load model: {e}")
    exit(1)

# ============================================================================
# PREPARE DATA
# ============================================================================

print("\n[2/6] Preparing validation data...")

# Validation data generator (không augmentation)
val_datagen = ImageDataGenerator(rescale=1./255)

val_generator = val_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False  # Không shuffle để giữ nguyên thứ tự
)

num_classes = val_generator.num_classes
class_names = list(val_generator.class_indices.keys())

print(f"✓ Số lượng người: {num_classes}")
print(f"✓ Tên các người: {', '.join(class_names)}")
print(f"✓ Validation samples: {val_generator.samples}")

# ============================================================================
# MAKE PREDICTIONS
# ============================================================================

print("\n[3/6] Making predictions...")

# Reset generator
val_generator.reset()

# Predict
predictions = model.predict(val_generator, verbose=1)
predicted_classes = np.argmax(predictions, axis=1)

# Get true labels
true_classes = val_generator.classes

print(f"✓ Predictions completed")
print(f"✓ Total predictions: {len(predicted_classes)}")

# ============================================================================
# CALCULATE METRICS
# ============================================================================

print("\n[4/6] Calculating metrics...")

# Overall accuracy
accuracy = accuracy_score(true_classes, predicted_classes)

# Precision, Recall, F1-Score (weighted average)
precision, recall, f1, support = precision_recall_fscore_support(
    true_classes, 
    predicted_classes, 
    average='weighted'
)

# Per-class metrics
precision_per_class, recall_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
    true_classes, 
    predicted_classes, 
    average=None,
    labels=range(num_classes)
)

print("\n" + "=" * 80)
print("KẾT QUẢ TỔNG QUÁT")
print("=" * 80)
print(f"Overall Accuracy:  {accuracy * 100:.2f}%")
print(f"Weighted Precision: {precision * 100:.2f}%")
print(f"Weighted Recall:    {recall * 100:.2f}%")
print(f"Weighted F1-Score:  {f1 * 100:.2f}%")
print("=" * 80)

# ============================================================================
# DETAILED CLASSIFICATION REPORT
# ============================================================================

print("\n[5/6] Generating classification report...")

print("\n" + "=" * 80)
print("CHI TIẾT THEO TỪNG NGƯỜI")
print("=" * 80)

report = classification_report(
    true_classes,
    predicted_classes,
    target_names=class_names,
    digits=4
)
print(report)

# ============================================================================
# CONFUSION MATRIX
# ============================================================================

print("\n[6/6] Creating confusion matrix...")

# Calculate confusion matrix
cm = confusion_matrix(true_classes, predicted_classes)

# Plot confusion matrix
plt.figure(figsize=(12, 10))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=class_names,
    yticklabels=class_names,
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save plot
cm_path = os.path.join(BASE_DIR, 'confusion_matrix.png')
plt.savefig(cm_path, dpi=150, bbox_inches='tight')
print(f"✓ Confusion matrix saved: {cm_path}")

# ============================================================================
# PLOT PER-CLASS METRICS
# ============================================================================

# Plot per-class metrics
plt.figure(figsize=(14, 6))

x = np.arange(num_classes)
width = 0.25

plt.bar(x - width, precision_per_class * 100, width, label='Precision', color='skyblue')
plt.bar(x, recall_per_class * 100, width, label='Recall', color='lightcoral')
plt.bar(x + width, f1_per_class * 100, width, label='F1-Score', color='lightgreen')

plt.xlabel('Person', fontsize=12)
plt.ylabel('Score (%)', fontsize=12)
plt.title('Per-Class Metrics', fontsize=16, fontweight='bold')
plt.xticks(x, class_names, rotation=45, ha='right')
plt.ylim(0, 105)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

metrics_path = os.path.join(BASE_DIR, 'per_class_metrics.png')
plt.savefig(metrics_path, dpi=150, bbox_inches='tight')
print(f"✓ Per-class metrics saved: {metrics_path}")

# ============================================================================
# SAVE DETAILED RESULTS
# ============================================================================

results = {
    'model_path': MODEL_PATH,
    'num_classes': num_classes,
    'num_samples': len(true_classes),
    'overall_metrics': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    },
    'per_class_metrics': {}
}

for i, name in enumerate(class_names):
    results['per_class_metrics'][name] = {
        'precision': float(precision_per_class[i]),
        'recall': float(recall_per_class[i]),
        'f1_score': float(f1_per_class[i]),
        'support': int(support_per_class[i])
    }

results_path = os.path.join(BASE_DIR, 'evaluation_results.json')
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✓ Detailed results saved: {results_path}")

# ============================================================================
# FIND MISCLASSIFIED SAMPLES
# ============================================================================

print("\n" + "=" * 80)
print("PHÂN TÍCH LỖI")
print("=" * 80)

misclassified_indices = np.where(predicted_classes != true_classes)[0]
print(f"Số mẫu bị phân loại sai: {len(misclassified_indices)} / {len(true_classes)}")
print(f"Tỷ lệ lỗi: {len(misclassified_indices) / len(true_classes) * 100:.2f}%")

if len(misclassified_indices) > 0:
    print("\nMột số ví dụ phân loại sai:")
    for i, idx in enumerate(misclassified_indices[:10]):  # Hiển thị 10 lỗi đầu
        true_label = class_names[true_classes[idx]]
        pred_label = class_names[predicted_classes[idx]]
        confidence = predictions[idx][predicted_classes[idx]] * 100
        print(f"  {i+1}. Sample {idx}: True='{true_label}' → Predicted='{pred_label}' (confidence: {confidence:.2f}%)")

# ============================================================================
# CONFIDENCE DISTRIBUTION
# ============================================================================

print("\n" + "=" * 80)
print("PHÂN BỐ ĐỘ TỰ TIN (CONFIDENCE)")
print("=" * 80)

max_confidences = np.max(predictions, axis=1)
correct_confidences = max_confidences[predicted_classes == true_classes]
incorrect_confidences = max_confidences[predicted_classes != true_classes]

print(f"Độ tự tin trung bình (đúng):  {np.mean(correct_confidences) * 100:.2f}%")
print(f"Độ tự tin trung bình (sai):   {np.mean(incorrect_confidences) * 100:.2f}%")
print(f"Độ tự tin cao nhất:           {np.max(max_confidences) * 100:.2f}%")
print(f"Độ tự tin thấp nhất:          {np.min(max_confidences) * 100:.2f}%")

# Plot confidence distribution
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(correct_confidences * 100, bins=20, color='green', alpha=0.7, label='Correct')
plt.hist(incorrect_confidences * 100, bins=20, color='red', alpha=0.7, label='Incorrect')
plt.xlabel('Confidence (%)')
plt.ylabel('Count')
plt.title('Confidence Distribution')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.subplot(1, 2, 2)
plt.boxplot([correct_confidences * 100, incorrect_confidences * 100],
            labels=['Correct', 'Incorrect'])
plt.ylabel('Confidence (%)')
plt.title('Confidence Box Plot')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
confidence_path = os.path.join(BASE_DIR, 'confidence_distribution.png')
plt.savefig(confidence_path, dpi=150, bbox_inches='tight')
print(f"✓ Confidence distribution saved: {confidence_path}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("TỔNG KẾT")
print("=" * 80)
print(f"✓ Model: {os.path.basename(MODEL_PATH)}")
print(f"✓ Accuracy: {accuracy * 100:.2f}%")
print(f"✓ Precision: {precision * 100:.2f}%")
print(f"✓ Recall: {recall * 100:.2f}%")
print(f"✓ F1-Score: {f1 * 100:.2f}%")
print(f"✓ Số người: {num_classes}")
print(f"✓ Tổng số mẫu test: {len(true_classes)}")
print(f"✓ Phân loại đúng: {np.sum(predicted_classes == true_classes)}")
print(f"✓ Phân loại sai: {len(misclassified_indices)}")
print("\nFiles đã tạo:")
print(f"  1. {cm_path}")
print(f"  2. {metrics_path}")
print(f"  3. {confidence_path}")
print(f"  4. {results_path}")
print("=" * 80)

plt.show()

print("\n🎉 ĐÁNH GIÁ HOÀN TẤT!")
