"""
Dọn Dẹp Project - Xóa Files Không Cần Thiết
"""

import os
import shutil

BASE_DIR = r"D:\DACN"

print("=" * 80)
print("🧹 DỌN DẸP PROJECT")
print("=" * 80)

# ============================================================================
# FILES CẦN XÓA
# ============================================================================

files_to_delete = {
    # ROOT LEVEL - Scripts test cũ
    "add_employee_no_retrain.py": "Script test cũ",
    "check_and_add_face_encoding_column.py": "Migration script cũ",
    "check_mapping.py": "Test script cũ",
    "check_thai_employee.py": "Test script cũ",
    "fix_photo_path.py": "Fix script cũ",
    "migrate_to_embedding.py": "Migration cũ (đã dùng xong)",
    "migrate_to_embedding_mtcnn.py": "Migration cũ",
    "quick_create_testuser.py": "Test script",
    "remove_session_checks.py": "Fix script cũ",
    "test_comprehensive_fix.py": "Test cũ",
    "test_final_mapping.py": "Test cũ",
    "test_mapping_fixed.py": "Test cũ",
    "test_model_load.py": "Test cũ",
    
    # Databases cũ
    "dacn.db": "SQLite cũ (đã chuyển MySQL)",
    "face_db.sqlite": "SQLite cũ",
    
    # AI FOLDER - Models cũ
    "DACN/AI/faceid_model_tf.h5": "CNN model cũ (67% accuracy)",
    "DACN/AI/faceid_model_tf_best.h5": "CNN model cũ",
    "DACN/AI/faceid_optimized_best.h5": "Model cũ",
    "DACN/AI/faceid_optimized_model.h5": "Model cũ",
    "DACN/AI/faceid_small_dataset_model.pkl": "Model failed (40%)",
    "DACN/AI/faceid_augmented_model.pkl": "Model failed (35%)",
    
    # Training scripts cũ
    "DACN/AI/train_ai_optimized.py": "Training cũ (67%)",
    "DACN/AI/train_faceid_improved.py": "Training cũ",
    "DACN/AI/train_faceid_improved_v2.py": "Training cũ",
    "DACN/AI/train_faceid_tensorflow.py": "Training cũ",
    "DACN/AI/train_improved.py": "Training cũ",
    "DACN/AI/train_small_dataset.py": "Training failed",
    "DACN/AI/train_with_external_data.py": "Training cũ",
    
    # Scripts cũ
    "DACN/AI/app_old.py": "Flask app cũ",
    "DACN/AI/app_improved.py": "Flask app cũ",
    "DACN/AI/augment_dataset.py": "Augmentation failed",
    "DACN/AI/download_dataset_auto.py": "Download script (không dùng)",
    "DACN/AI/download_lfw_dataset.py": "Download script (không dùng)",
    "DACN/AI/create_synthetic_dataset.py": "Không dùng",
    "DACN/AI/collect_face_data.py": "Có script mới tốt hơn",
    "DACN/AI/test_small_model.py": "Test model cũ",
    "DACN/AI/test_external_model_webcam.py": "Test cũ",
    "DACN/AI/update_embeddings_small.py": "Update cũ",
    "DACN/AI/update_embeddings_to_db.py": "Update cũ",
    "DACN/AI/export_embedding_model.py": "Không cần",
    "DACN/AI/evaluate_model.py": "Có script mới",
    "DACN/AI/monitor_training.py": "Không dùng",
    
    # Database files cũ
    "DACN/AI/faces.db": "SQLite cũ",
    "DACN/AI/face_db.sqlite": "SQLite cũ",
    "DACN/AI/face_embeddings_db.pkl": "Pickle cũ",
    "DACN/AI/face_embeddings_external.pkl": "Pickle cũ",
    
    # Data cũ
    "DACN/AI/class_mapping.json": "Mapping cũ",
    "DACN/AI/evaluation_results.json": "Results cũ",
    
    # Images cũ
    "DACN/AI/confusion_matrix.png": "Plot cũ",
    "DACN/AI/confidence_distribution.png": "Plot cũ",
    "DACN/AI/per_class_metrics.png": "Plot cũ",
    "DACN/AI/training_history.png": "Plot cũ",
}

# ============================================================================
# FOLDERS CẦN XÓA
# ============================================================================

folders_to_delete = {
    "DACN/AI/face_data_augmented": "Augmented data failed",
    "DACN/AI/lfw_download": "LFW dataset (không dùng)",
    "DACN/AI/AI": "Folder trùng",
    "DACN/AI/logs": "Logs cũ",
    "AI": "Folder trùng ở root",
}

# ============================================================================
# EXECUTE DELETION
# ============================================================================

deleted_count = 0
skipped_count = 0

print("\n[1/2] Deleting files...")
for file_path, reason in files_to_delete.items():
    full_path = os.path.join(BASE_DIR, file_path)
    
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            print(f"  ✅ Deleted: {file_path}")
            print(f"     Reason: {reason}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed: {file_path} - {e}")
            skipped_count += 1
    else:
        print(f"  ⏭️  Skip (not found): {file_path}")
        skipped_count += 1

print("\n[2/2] Deleting folders...")
for folder_path, reason in folders_to_delete.items():
    full_path = os.path.join(BASE_DIR, folder_path)
    
    if os.path.exists(full_path):
        try:
            shutil.rmtree(full_path)
            print(f"  ✅ Deleted: {folder_path}")
            print(f"     Reason: {reason}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ Failed: {folder_path} - {e}")
            skipped_count += 1
    else:
        print(f"  ⏭️  Skip (not found): {folder_path}")
        skipped_count += 1

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("🎉 DỌN DẸP HOÀN TẤT!")
print("=" * 80)
print(f"✅ Deleted: {deleted_count} items")
print(f"⏭️  Skipped: {skipped_count} items")

print("\n📁 FILES GIỮ LẠI (QUAN TRỌNG):")
print("=" * 80)

important_files = {
    "Model hiện tại": [
        "DACN/AI/faceid_best_model.pkl",
        "DACN/AI/faceid_best_model_metadata.pkl",
    ],
    "Scripts hiện tại": [
        "DACN/AI/app.py",
        "DACN/AI/train_best_model.py",
        "DACN/AI/test_best_model_webcam.py",
        "DACN/AI/update_embeddings_best_model.py",
        "DACN/AI/check_attendance.py",
        "DACN/AI/monitor_realtime.py",
        "DACN/AI/evaluate_model_accuracy.py",
    ],
    "Data": [
        "DACN/AI/face_data/",
    ],
    "Desktop App": [
        "DACN/faceid_desktop/main.py",
    ],
    "Documentation": [
        "ACCURACY_REPORT.md",
        "INTEGRATION_REPORT.md",
        "FIX_NAME_MAPPING.md",
        "UI_FIX_SUMMARY.md",
        "QUICK_START.md",
    ],
}

for category, files in important_files.items():
    print(f"\n{category}:")
    for f in files:
        print(f"  ✅ {f}")

print("\n" + "=" * 80)
print("✅ PROJECT ĐÃ SẠCH SẼ!")
print("=" * 80)
