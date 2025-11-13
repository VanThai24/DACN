# NGUỒN DỮ LIỆU KHUÔN MẶT - FACE DATASETS

## 🌟 CÁC DATASET PHỔ BIẾN

### 1. **LFW (Labeled Faces in the Wild)** ⭐⭐⭐⭐⭐
**URL:** http://vis-www.cs.umass.edu/lfw/

**Mô tả:**
- 13,000+ ảnh khuôn mặt
- 5,749 người
- Ảnh trong môi trường tự nhiên
- Chất lượng cao

**Download:**
```bash
# Direct link
wget http://vis-www.cs.umass.edu/lfw/lfw.tgz
```

**Sử dụng:**
- ✅ Research & Development
- ✅ Non-commercial use
- ⚠️ Cần citation nếu publish

---

### 2. **CelebA (CelebFaces Attributes)** ⭐⭐⭐⭐⭐
**URL:** https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html

**Mô tả:**
- 200,000+ ảnh
- 10,000+ người nổi tiếng
- 40 attributes (kính, râu, giới tính, etc.)
- Đa dạng góc độ, ánh sáng

**Download:**
- Google Drive: https://drive.google.com/drive/folders/0B7EVK8r0v71pWEZsZE9oNnFzTm8
- Kaggle: https://www.kaggle.com/datasets/jessicali9530/celeba-dataset

**Sử dụng:**
- ✅ Research
- ✅ Education
- ❌ Commercial (cần license)

---

### 3. **VGGFace2** ⭐⭐⭐⭐⭐
**URL:** https://github.com/ox-vgg/vgg_face2

**Mô tả:**
- 3.31M ảnh
- 9,131 người
- Đa dạng về age, pose, illumination
- Dataset chất lượng cao nhất

**Download:**
```python
# Cần request access qua Google Form
# Link: https://forms.gle/xxxxxx
```

**Sử dụng:**
- ✅ Research
- ✅ Non-commercial
- ⚠️ Cần registration

---

### 4. **CASIA-WebFace** ⭐⭐⭐⭐
**URL:** http://www.cbsr.ia.ac.cn/english/CASIA-WebFace-Database.html

**Mô tả:**
- 500,000 ảnh
- 10,575 người
- Crawled từ IMDb
- Free download

**Download:**
- Baidu Pan (China)
- Google Drive mirrors

---

### 5. **MS-Celeb-1M** ⭐⭐⭐⭐
**URL:** https://www.microsoft.com/en-us/research/project/ms-celeb-1m-challenge-recognizing-one-million-celebrities-real-world/

**Mô tả:**
- 10M ảnh
- 100K người nổi tiếng
- Từ Microsoft Research
- ⚠️ Đã bị gỡ xuống vì privacy issues

**Alternative:**
- Tìm mirrors trên academic sites
- Một số subset còn available

---

## 🎯 DATASET CHO DỰ ÁN ATTENDANCE (KHUYẾN NGHỊ)

### 6. **UTKFace** ⭐⭐⭐⭐⭐ (TỐT NHẤT CHO BẠN)
**URL:** https://susanqq.github.io/UTKFace/

**Mô tả:**
- 20,000+ ảnh
- Diverse ages, races, genders
- Single face per image
- High quality frontal faces
- **PHÙ HỢP CHO ATTENDANCE SYSTEM!**

**Download:**
```bash
# Kaggle (Dễ nhất)
kaggle datasets download -d jangedoo/utkface-new

# Direct
wget https://drive.google.com/file/d/xxxxxx
```

**Ưu điểm cho bạn:**
- ✅ Khuôn mặt thẳng (frontal)
- ✅ Đa dạng ethnicity
- ✅ Free & Open
- ✅ Không cần registration

---

### 7. **Pins Face Recognition** ⭐⭐⭐⭐
**URL:** https://www.kaggle.com/datasets/hereisburak/pins-face-recognition

**Mô tả:**
- 105 người
- 17,534 ảnh
- Real-world quality
- Kaggle dataset

**Download:**
```bash
kaggle datasets download -d hereisburak/pins-face-recognition
```

---

### 8. **Real-World Face Mask Dataset** ⭐⭐⭐⭐
**URL:** https://www.kaggle.com/datasets/andrewmvd/face-mask-detection

**Mô tả:**
- 853 ảnh
- Có/không khẩu trang
- Good cho COVID-19 era attendance

---

## 🚀 CÁCH SỬ DỤNG DATASETS

### Option 1: Download Subset Nhỏ

**Tạo script download từ LFW:**

```python
# download_lfw_subset.py
import urllib.request
import tarfile
import os
import shutil

# Download LFW
url = "http://vis-www.cs.umass.edu/lfw/lfw.tgz"
filename = "lfw.tgz"

print("Downloading LFW dataset...")
urllib.request.urlretrieve(url, filename)

print("Extracting...")
with tarfile.open(filename, 'r:gz') as tar:
    tar.extractall()

# Chọn random 6 người, mỗi người 50 ảnh
import random
from glob import glob

lfw_dir = "lfw"
output_dir = "face_data"
os.makedirs(output_dir, exist_ok=True)

persons = [d for d in os.listdir(lfw_dir) 
          if os.path.isdir(os.path.join(lfw_dir, d))]

# Filter: chỉ lấy người có ≥50 ảnh
persons_with_enough_images = []
for person in persons:
    person_dir = os.path.join(lfw_dir, person)
    images = glob(os.path.join(person_dir, "*.jpg"))
    if len(images) >= 50:
        persons_with_enough_images.append(person)

# Random chọn 6 người
selected = random.sample(persons_with_enough_images, 6)

for person in selected:
    src_dir = os.path.join(lfw_dir, person)
    dst_dir = os.path.join(output_dir, person)
    os.makedirs(dst_dir, exist_ok=True)
    
    # Copy 50 ảnh đầu
    images = glob(os.path.join(src_dir, "*.jpg"))[:50]
    for img in images:
        shutil.copy(img, dst_dir)
    
    print(f"✅ {person}: {len(images)} ảnh")

print(f"\n✅ Done! Dataset saved to: {output_dir}")
```

---

### Option 2: Download từ Kaggle (DỄ NHẤT)

**1. Setup Kaggle API:**
```powershell
# Install kaggle
pip install kaggle

# Get API token từ https://www.kaggle.com/settings
# Download kaggle.json
# Move to: C:\Users\<YourName>\.kaggle\kaggle.json
```

**2. Download datasets:**
```powershell
# UTKFace
kaggle datasets download -d jangedoo/utkface-new
Expand-Archive utkface-new.zip -DestinationPath face_data_utkface

# Pins Face Recognition
kaggle datasets download -d hereisburak/pins-face-recognition
Expand-Archive pins-face-recognition.zip -DestinationPath face_data_pins
```

**3. Process data:**
```python
# process_kaggle_data.py
import os
import shutil
import random

src_dir = "face_data_pins/105_classes_pins_dataset"
dst_dir = "face_data"

# Lấy 6 người random
persons = os.listdir(src_dir)
selected = random.sample(persons, 6)

for person in selected:
    src_person = os.path.join(src_dir, person)
    dst_person = os.path.join(dst_dir, person.replace(" ", "_"))
    
    # Copy tất cả ảnh (hoặc giới hạn 50)
    shutil.copytree(src_person, dst_person)
    
print("✅ Done!")
```

---

## 🎨 CÔNG CỤ TẠO SYNTHETIC DATA

### 1. **This Person Does Not Exist**
**URL:** https://thispersondoesnotexist.com/

**Cách dùng:**
- Reload page → Face mới được generate bởi GAN
- Save image
- Lặp lại 50 lần cho mỗi "người" (nhưng sẽ khác nhau)

⚠️ **Lưu ý:** Không tốt cho attendance vì mỗi ảnh là người khác nhau!

---

### 2. **Generated.photos**
**URL:** https://generated.photos/

**Mô tả:**
- 100,000 fake faces
- API có thể query theo attributes
- Có thể generate consistent faces

**API:**
```python
import requests

api_key = "YOUR_API_KEY"
url = f"https://api.generated.photos/api/v1/faces"

params = {
    "age": "young-adult",
    "gender": "male",
    "per_page": 50
}

headers = {"Authorization": f"API-Key {api_key}"}
response = requests.get(url, params=params, headers=headers)
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### 1. **Về Mặt Pháp Lý:**

- ✅ **Được phép:** Research, education, non-commercial
- ⚠️ **Cần citation:** Most academic datasets
- ❌ **Không được:** Commercial use without license
- ❌ **Privacy issues:** Một số dataset đã bị gỡ (MS-Celeb-1M)

### 2. **Về Chất Lượng:**

**Datasets công khai ≠ Dữ liệu thật của bạn**

Vấn đề:
- ❌ Không giống người thật trong company
- ❌ Lighting/camera khác
- ❌ Model học features không phù hợp

**Giải pháp tốt nhất:**
- ✅ **THU THẬP DỮ LIỆU THẬT** từ 6 người
- ✅ Dùng `collect_face_data.py` đã tạo
- ✅ 50 ảnh/người, 1 giờ là xong
- ✅ Accuracy sẽ là 90-95%

Nếu dùng dataset công khai:
- ⚠️ Chỉ để **practice/demo**
- ⚠️ Phải **fine-tune** với real data sau
- ⚠️ Accuracy trên real data sẽ thấp hơn

---

## 🎯 KHUYẾN NGHỊ CHO BẠN

### Option A: Dùng Dataset Công Khai (Demo/Practice)

**Tốt nhất:** UTKFace hoặc Pins Face Recognition

```powershell
# 1. Download từ Kaggle
kaggle datasets download -d hereisburak/pins-face-recognition

# 2. Extract và chọn 6 người
python process_kaggle_data.py

# 3. Train
python train_small_dataset.py
```

**Ưu điểm:**
- ✅ Nhanh (30 phút)
- ✅ Không cần người thật

**Nhược điểm:**
- ❌ Không hoạt động tốt với người thật
- ❌ Chỉ để demo

---

### Option B: Thu Thập Dữ Liệu Thật (Production)

```powershell
# 1. Thu thập từ 6 người thật
python collect_face_data.py

# 2. Train
python train_small_dataset.py
```

**Ưu điểm:**
- ✅ Accuracy cao (90-95%)
- ✅ Sẵn sàng production
- ✅ Hoạt động với real users

**Nhược điểm:**
- ⏰ Cần 1 giờ
- 👥 Cần 6 người

---

## 📚 TÀI NGUYÊN THÊM

### Papers về Face Recognition Datasets:
- LFW: http://vis-www.cs.umass.edu/lfw/lfw.pdf
- VGGFace2: https://arxiv.org/abs/1710.08092
- MS-Celeb-1M: https://arxiv.org/abs/1607.08221

### GitHub Repos với Pre-downloaded Data:
- https://github.com/ageitgey/face_recognition (includes sample data)
- https://github.com/deepinsight/insightface (model zoo with datasets)

---

## 🚀 SCRIPT TỰ ĐỘNG DOWNLOAD

Tôi có thể tạo script tự động download và process dataset cho bạn. 

**Bạn muốn dataset nào?**
1. UTKFace (20K ảnh, đa dạng)
2. Pins Face (105 người, real-world)
3. LFW (academic standard)
4. CelebA (celebrities)

Cho tôi biết và tôi sẽ tạo script download + process ngay! 🎯

---

## 💡 KẾT LUẬN

**Cho Demo/Practice:** Dùng Kaggle datasets (Pins Face hoặc UTKFace)

**Cho Production:** THU THẬP DỮ LIỆU THẬT từ 6 người (1 giờ)

**Best Practice:** Demo với public data → Deploy với real data

Bạn muốn tôi tạo script download dataset nào không? 🚀
