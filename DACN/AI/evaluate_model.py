import os
import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'face_data')
MODEL_PATH = os.path.join(BASE_DIR, 'faceid_model_tf.h5')

IMG_SIZE = (128, 128)
BATCH_SIZE = 32

# Load model
print("Loading model...")
model = keras.models.load_model(MODEL_PATH)
print(f"Model loaded successfully!")

# Tạo data generator để test
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

print(f"\nFound {test_generator.samples} images belonging to {test_generator.num_classes} classes")
print(f"Classes: {list(test_generator.class_indices.keys())}")

# Đánh giá mô hình
print("\nEvaluating model...")
loss, accuracy = model.evaluate(test_generator, verbose=1)

print(f"\n{'='*50}")
print(f"Model Performance:")
print(f"{'='*50}")
print(f"Loss: {loss:.4f}")
print(f"Accuracy: {accuracy*100:.2f}%")
print(f"{'='*50}")

# Thông tin về embedding
print(f"\nEmbedding layer info:")
embedding_layer = model.layers[-2]  # Layer trước softmax
print(f"Layer name: {embedding_layer.name}")
print(f"Output shape: {embedding_layer.output_shape}")
print(f"Embedding size: {embedding_layer.output_shape[1]} dimensions")
