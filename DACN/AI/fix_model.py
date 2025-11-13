"""
Script fix model đã train: thêm output_shape cho Lambda layer
để có thể load được model mà không cần train lại
"""
import tensorflow as tf
from tensorflow.keras import layers, models
import os

# Custom function cho L2 normalization
def l2_normalize_func(x):
    """L2 normalization function"""
    return tf.nn.l2_normalize(x, axis=1)

# Path model cần fix
MODEL_PATH = 'D:/DACN/DACN/AI/AI/faceid_model_tf_best.h5'
OUTPUT_PATH = 'D:/DACN/DACN/AI/faceid_model_tf_best_fixed.h5'

print(f"Loading model from: {MODEL_PATH}")

# Load model cũ (với safe_mode=False và custom_objects)
old_model = tf.keras.models.load_model(MODEL_PATH, safe_mode=False, custom_objects={'l2_normalize_func': l2_normalize_func})

print("✓ Model loaded successfully")
print(f"Model summary:")
old_model.summary()

# Rebuild model với output_shape trong Lambda
inputs = old_model.input

# Lấy embedding layer trước Lambda
embedding_layer_output = old_model.get_layer('embedding_128').output

# Tạo Lambda layer mới với output_shape
embedding_normalized = layers.Lambda(
    lambda x: tf.nn.l2_normalize(x, axis=1),
    output_shape=(128,),
    name='embedding_normalized_fixed'
)(embedding_layer_output)

# Lấy classification layer
classification_weights = old_model.get_layer('classification').get_weights()
num_classes = classification_weights[0].shape[1]

outputs = layers.Dense(num_classes, activation='softmax', name='classification')(embedding_normalized)

# Build model mới
new_model = models.Model(inputs=inputs, outputs=outputs, name='FaceID_MobileNetV2_Fixed')

# Copy weights từ old model
for layer in new_model.layers:
    if layer.name == 'embedding_normalized_fixed':
        continue  # Skip Lambda layer (không có weights)
    
    try:
        old_layer = old_model.get_layer(layer.name)
        layer.set_weights(old_layer.get_weights())
        print(f"✓ Copied weights for layer: {layer.name}")
    except:
        print(f"  Skipped layer: {layer.name}")

print("\n" + "="*60)
print("Saving fixed model...")
print("="*60)

# Save model mới
new_model.save(OUTPUT_PATH)
print(f"✓ Saved to: {OUTPUT_PATH}")

# Test load lại
print("\nTesting load...")
test_model = tf.keras.models.load_model(OUTPUT_PATH, custom_objects={'l2_normalize_func': l2_normalize_func})
print("✓ Fixed model can be loaded successfully!")

print("\n✓ Done! Use this model in app.py")
