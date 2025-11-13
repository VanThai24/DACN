"""
Kiểm tra output shape của TensorFlow model
"""
import tensorflow as tf
from pathlib import Path

# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

MODEL_PATH = Path(__file__).parent / "faceid_model_tf.h5"

print(f"📂 Loading model: {MODEL_PATH}")
model = tf.keras.models.load_model(str(MODEL_PATH), custom_objects={'l2_normalize_func': l2_normalize_func})

print("\n📊 Model Summary:")
model.summary()

print(f"\n🔍 Model output shape: {model.output_shape}")
print(f"📏 Embedding dimension: {model.output_shape[-1]}")

if model.output_shape[-1] == 128:
    print("\n✅ Model output đúng 128 chiều!")
else:
    print(f"\n❌ CẢNH BÁO: Model output chỉ {model.output_shape[-1]} chiều!")
    print("   Face recognition cần 128 chiều để so sánh!")
