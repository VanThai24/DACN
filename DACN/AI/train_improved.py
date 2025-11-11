import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Đường dẫn dữ liệu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'face_data')

# Cấu hình
IMG_SIZE = (128, 128)
BATCH_SIZE = 16  # Giảm batch size để ổn định hơn
EPOCHS = 50

print("="*60)
print("TRAINING IMPROVED FACE RECOGNITION MODEL WITH VGG16")
print("="*60)

# Data augmentation mạnh để tăng số lượng ảnh
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.2,
    zoom_range=0.3,
    brightness_range=[0.5, 1.5],
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # 20% cho validation
)

# Training data
train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True,
    subset='training'
)

# Validation data
val_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
    subset='validation'
)

print(f"\nTraining samples: {train_generator.samples}")
print(f"Validation samples: {val_generator.samples}")
print(f"Number of classes: {train_generator.num_classes}")
print(f"Classes: {list(train_generator.class_indices.keys())}")

# Sử dụng VGG16 pre-trained (đã học từ ImageNet)
print("\nLoading VGG16 base model...")
base_model = VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(*IMG_SIZE, 3)
)

# Freeze các layer của VGG16 (không train lại)
base_model.trainable = False

# Xây dựng model mới với VGG16 làm feature extractor
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),  # Embedding layer
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(train_generator.num_classes, activation='softmax')
])

# Compile model
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\nModel architecture:")
model.summary()

# Callbacks
early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

checkpoint = ModelCheckpoint(
    'faceid_model_tf_improved.h5',
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

# Train model
print("\n" + "="*60)
print("STARTING TRAINING...")
print("="*60 + "\n")

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=[early_stop, checkpoint],
    verbose=1
)

# Đánh giá model
print("\n" + "="*60)
print("EVALUATION ON VALIDATION SET")
print("="*60)
val_loss, val_accuracy = model.evaluate(val_generator, verbose=1)

print(f"\n{'='*60}")
print(f"FINAL RESULTS:")
print(f"{'='*60}")
print(f"Validation Loss: {val_loss:.4f}")
print(f"Validation Accuracy: {val_accuracy*100:.2f}%")
print(f"{'='*60}")

# Lưu model cuối cùng
model.save('faceid_model_tf.h5')
print("\n✅ Model saved as 'faceid_model_tf.h5'")

# Hiển thị training history
print(f"\nBest validation accuracy: {max(history.history['val_accuracy'])*100:.2f}%")
print(f"Final training accuracy: {history.history['accuracy'][-1]*100:.2f}%")
