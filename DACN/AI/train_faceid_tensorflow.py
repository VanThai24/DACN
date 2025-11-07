
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

# Đường dẫn dữ liệu tuyệt đối, luôn đúng dù chạy từ đâu
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
BATCH_SIZE = 32
EPOCHS = 40  # Tăng số epoch để model học tốt hơn


# Tạo ImageDataGenerator với data augmentation cho train và validation split

# Tăng cường dữ liệu tối đa cho trường hợp rất ít ảnh
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=60,
    width_shift_range=0.4,
    height_shift_range=0.4,
    shear_range=0.3,
    zoom_range=0.4,
    brightness_range=[0.3, 1.5],
    channel_shift_range=50.0,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest',
    validation_split=0.0  # Không chia validation vì quá ít ảnh
)

train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_generator = None  # Không dùng validation khi quá ít ảnh


# Xây dựng model CNN cải tiến với Dropout
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(train_generator.num_classes, activation='softmax')
])


model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# EarlyStopping để tránh overfitting
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Huấn luyện model không dùng validation nếu quá ít ảnh
model.fit(
    train_generator,
    epochs=EPOCHS,
    callbacks=[early_stop]
)


# Lưu model
model.save('AI/faceid_model_tf.h5')
print('Đã lưu model vào AI/faceid_model_tf.h5')
