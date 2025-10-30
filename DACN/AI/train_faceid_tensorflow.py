import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Đường dẫn dữ liệu
DATA_DIR = 'AI/face_data'

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
EPOCHS = 20

# Tạo ImageDataGenerator cho train và validation

train_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

# Xây dựng model CNN đơn giản
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D(2, 2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(train_generator.num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Huấn luyện model
model.fit(
    train_generator,
    epochs=EPOCHS
)

# Lưu model
model.save('AI/faceid_model_tf.h5')
print('Đã lưu model vào AI/faceid_model_tf.h5')
