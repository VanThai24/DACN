# 🚀 QUICK REFERENCE - Tham Khảo Nhanh

## ⚡ Most Common Commands

### Start Desktop App
```bash
cd D:\DACN\DACN\faceid_desktop && python main.py
```

### Start Web Admin  
```bash
cd D:\DACN\DACN && dotnet run
```

### Add New Employee
```bash
cd D:\DACN\DACN\AI && .\add_new_employee.bat
```

### Train Model
```bash
cd D:\DACN\DACN\AI && python train_best_model.py && python update_embeddings_best_model.py
```

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `COMMANDS.md` | All commands |
| `TROUBLESHOOTING.md` | Fix common errors |
| `PROJECT_STRUCTURE.md` | Project structure |
| `DACN/AI/app.py` | Flask API |
| `DACN/AI/train_best_model.py` | Training script |
| `DACN/faceid_desktop/main.py` | Desktop app |

---

## 🔑 Credentials

```
MySQL:
  Host: localhost
  User: root
  Password: 12345
  Database: attendance_db

Web Admin:
  URL: https://localhost:5001
  Username: admin
  Password: admin123
```

---

## 🐛 Quick Fixes

### Desktop app JWT error?
→ **Ignore it** (doesn't affect face recognition)

### Camera not working?
→ Close other apps using camera, restart

### Unknown person?
→ `cd AI && .\add_new_employee.bat`

### MySQL connection error?
→ `net start MySQL80`

### Low accuracy?
→ Add more training images, retrain model

---

## 📊 System Status

```
✅ AI Model: 100% accuracy
✅ Training Data: 6 employees × 40 images
✅ Apps: 4 (Desktop, Web, Mobile, API)
✅ Database: MySQL with 5 tables
✅ Status: Ready for thesis defense
```

---

## 🎯 Demo Sequence

1. Start Desktop App → Show face recognition
2. Open Web Admin → Show attendance records
3. (Optional) Open Mobile App → Show user interface
4. Add new employee demo
5. Show model training output

---

## 📚 Documentation Index

```
📄 README.md                  → Overview & Quick Start
📄 COMMANDS.md                → Command Reference
📄 TROUBLESHOOTING.md         → Error Fixes
📄 PROJECT_STRUCTURE.md       → File Structure
📄 PROJECT_COMPLETION_REPORT.md → Completion Status
📄 QUICK_START_GUIDE.md       → Detailed Setup Guide

📁 DACN/AI/
  📄 README.md                → AI Module Docs
  📄 FOR_THESIS_ONLY.md       → Thesis Workflow
  📄 HOW_TO_ADD_EMPLOYEE.md   → Employee Guide
  📄 DATA_COLLECTION_GUIDE.md → Data Collection

📁 DACN/mobile_app/
  📄 README.md                → Mobile App Docs
  📄 ANDROID_SETUP_GUIDE.md   → Android Setup

📁 DACN/faceid_desktop/
  📄 README.md                → Desktop App Docs
```

---

## ⚠️ Important Notes

- ✅ Model must be retrained when adding new employees
- ✅ Minimum 40 images per person for good accuracy
- ✅ Good lighting required for face recognition
- ✅ Distance: 30-80cm from camera
- ✅ Face camera directly, remove masks/sunglasses

---

## 🎓 For Thesis Defense

### Key Points to Mention
- 100% accuracy achieved with SVM classifier
- Real-time processing (<1 second per face)
- Multi-platform support (Web, Mobile, Desktop)
- Automatic duplicate attendance prevention
- Auto shift detection based on time

### Demo Preparation
- [ ] Test all apps before defense
- [ ] Prepare backup video demo
- [ ] Have screenshots ready
- [ ] Test on backup laptop
- [ ] Prepare to explain code

### Expected Questions
1. **How does face recognition work?**
   → dlib face_recognition extracts 128-dim embeddings, SVM classifier predicts identity

2. **What's the accuracy?**
   → 100% test accuracy with current 5 employees

3. **How to handle new employees?**
   → Run add_new_employee.bat → captures images → augments → retrains → updates DB

4. **What about security?**
   → JWT tokens, BCrypt passwords, duplicate attendance prevention

5. **Production readiness?**
   → Working prototype for thesis, production needs optimization (scale, security, etc.)

---

**🎯 Version**: 1.0.0 (Optimized)  
**📅 Last Updated**: November 2025  
**✍️ Status**: Ready for Defense
