import cv2
import os

# Test face detection trên tất cả ảnh của Huy
face_data_path = '../AI/face_data/Huy'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

for img_name in sorted(os.listdir(face_data_path))[:5]:
    img_path = os.path.join(face_data_path, img_name)
    img = cv2.imread(img_path)
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
        print(f"{img_name}: {len(faces)} faces detected")
