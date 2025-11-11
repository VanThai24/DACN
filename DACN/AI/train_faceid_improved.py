
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# Đường dẫn dữ liệu tuyệt đối
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'face_data')

# Chỉ giữ lại file ảnh (jpg, jpeg, png) trong các thư mục con
def allowed_file(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.png'))

for class_name in os.listdir(DATA_DIR):
    class_path = os.path.join(DATA_DIR, class_name)
    if os.path.isdir(class_path):
        for fname in os.listdir(class_path):
            if not allowed_file(fname):
                try:
                    os.remove(os.path.join(class_path, fname))
                except Exception:
                    pass

IMG_SIZE = (128, 128)
BATCH_SIZE = 16  # Giảm batch size để model học tốt hơn với ít dữ liệu
EPOCHS = 100  # Tăng epochs

# Data augmentation CỰC MẠNH để tăng đa dạng dữ liệu
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.3,
    height_shift_range=0.3,
    shear_range=0.3,
    zoom_range=0.3,
    brightness_range=[0.5, 1.5],
    channel_shift_range=30.0,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # 20% cho validation
)

train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True,
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
    subset='validation'
)

print(f"Training samples: {train_generator.samples}")
print(f"Validation samples: {val_generator.samples}")
print(f"Classes: {train_generator.num_classes}")

# Xây dựng model CNN ĐƠN GIẢN HƠN cho dataset nhỏ
model = models.Sequential([
    # Block 1
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
    layers.MaxPooling2D(2, 2),
    layers.Dropout(0.25),
    
    # Block 2
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Dropout(0.25),
    
    # Block 3
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Dropout(0.25),
    
    # Dense layers với embedding layer 128 chiều (giảm từ 256)
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu', name='embedding_layer'),  # EMBEDDING 128 chiều
    layers.Dropout(0.4),
    layers.Dense(train_generator.num_classes, activation='softmax')
])

# Compile với learning rate cao hơn cho model đơn giản
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Callbacks để cải thiện training
callbacks = [
    # Dừng sớm nếu validation loss không giảm
    EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    # Giảm learning rate khi validation loss không giảm
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.00001,
        verbose=1
    ),
    # Lưu model tốt nhất
    ModelCheckpoint(
        'AI/faceid_model_tf_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# Huấn luyện model
print("\n" + "="*50)
print("Starting training...")
print("="*50 + "\n")

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# Đánh giá kết quả cuối cùng
print("\n" + "="*50)
print("Final Evaluation on Validation Set:")
print("="*50)
val_loss, val_accuracy = model.evaluate(val_generator, verbose=0)
print(f"Validation Loss: {val_loss:.4f}")
print(f"Validation Accuracy: {val_accuracy*100:.2f}%")
print("="*50 + "\n")

# Lưu model cuối cùng
model.save('AI/faceid_model_tf.h5')
print('Đã lưu model vào AI/faceid_model_tf.h5')
print(f'Model tốt nhất đã được lưu vào AI/faceid_model_tf_best.h5')

# In thông tin về embedding
print(f"\nEmbedding layer: 256 dimensions")
print("Sử dụng layer 'embedding_layer' để trích xuất đặc trưng khuôn mặt")
