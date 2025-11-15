import joblib

# Load model metadata
metadata = joblib.load('faceid_best_model_metadata.pkl')

print("=" * 60)
print("📊 MODEL ACCURACY - ĐỘ CHÍNH XÁC HIỆN TẠI")
print("=" * 60)
print()
print(f"✅ Train Accuracy:      {metadata['train_accuracy']*100:.2f}%")
print(f"✅ Test Accuracy:       {metadata['test_accuracy']*100:.2f}%")
print()
print(f"💪 Average Confidence:  {metadata['avg_confidence']*100:.2f}%")
if 'std_confidence' in metadata:
    print(f"📊 Std Confidence:      ±{metadata['std_confidence']*100:.2f}%")
print()
print(f"👥 Number of Classes:   {len(metadata['classes'])} employees")
print(f"📝 Employee Names:      {', '.join(metadata['classes'])}")
print()
print(f"⚙️  Best Hyperparameters:")
print(f"   - C:      {metadata['best_params']['C']}")
print(f"   - gamma:  {metadata['best_params']['gamma']}")
print(f"   - kernel: {metadata['best_params']['kernel']}")
print()
print("=" * 60)
