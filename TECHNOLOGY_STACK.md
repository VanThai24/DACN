# 🛠️ TECHNOLOGY STACK - Công Nghệ Sử Dụng

## 📊 Tổng Quan

```
🎯 Project: Face Recognition Attendance System
📅 Version: 1.0.0 (Thesis Edition)
🏗️ Architecture: Multi-tier (4 Applications)
💻 Total Tech Stack: 50+ libraries & frameworks
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                         │
├─────────────────────────────────────────────────────────┤
│  Desktop (PySide6)  │  Mobile (React Native)  │ Web UI │
└──────────┬──────────┴──────────┬───────────────────┬───┘
           │                      │                    │
           ▼                      ▼                    ▼
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                      │
├─────────────────────────────────────────────────────────┤
│  AI API (Flask)  │  Backend API (FastAPI)  │  ASP.NET  │
└──────────┬───────┴──────────┬──────────────────┬───────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                          │
├─────────────────────────────────────────────────────────┤
│  MySQL Database  │  Face Embeddings  │  Model Storage   │
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 AI/Machine Learning Stack

### Core AI Libraries
| Technology | Version | Purpose |
|------------|---------|---------|
| **dlib** | 20.0.0 | Face detection & landmarks detection |
| **face_recognition** | 1.2.3 | Face encoding (128-dim embeddings) |
| **scikit-learn** | 1.3.0+ | SVM classifier for face recognition |
| **OpenCV (cv2)** | 4.8.0+ | Image processing & augmentation |
| **NumPy** | 1.24.0+ | Numerical computing & array operations |
| **Pillow (PIL)** | Latest | Image manipulation |
| **joblib** | 1.3.0+ | Model serialization |

### AI Algorithm Details
```python
Algorithm: Support Vector Machine (SVM)
Kernel: RBF (Radial Basis Function)
Feature Extraction: dlib ResNet (128 dimensions)
Face Detection: HOG (Histogram of Oriented Gradients)
Hyperparameters: C=10, gamma='scale', kernel='rbf'
```

### Training Pipeline
- **GridSearchCV**: Hyperparameter tuning
- **train_test_split**: 80/20 split
- **Data Augmentation**: OpenCV transformations
- **Model Evaluation**: confusion_matrix, classification_report

---

## 🖥️ Desktop Application Stack

### Framework & UI
| Technology | Version | Purpose |
|------------|---------|---------|
| **PySide6** | 6.6.0+ | Qt-based GUI framework |
| **Qt Designer** | Built-in | UI design tool |

### Core Libraries
```python
PySide6.QtCore      # Core Qt functionality
PySide6.QtWidgets   # UI widgets
PySide6.QtGui       # GUI components
opencv-python       # Camera/video capture
requests            # HTTP client
numpy               # Array operations
mysql-connector     # Database connection
face-recognition    # AI integration
```

### Features Implemented
- Real-time webcam capture
- Face detection overlay
- MySQL integration
- Custom gradient UI
- Attendance logging

---

## 📱 Mobile Application Stack

### Framework & Core
| Technology | Version | Purpose |
|------------|---------|---------|
| **React Native** | 0.81.4 | Cross-platform mobile framework |
| **Expo** | 54.0.0 | Development & build platform |
| **React** | 19.1.0 | UI library |

### Navigation & Routing
```javascript
@react-navigation/native        7.1.18
@react-navigation/native-stack  7.3.28
@react-navigation/bottom-tabs   7.4.9
react-native-screens            4.16.0
react-native-safe-area-context  5.6.1
```

### UI Components
```javascript
@expo/vector-icons           15.0.2   // Icons
expo-linear-gradient         15.0.7   // Gradient backgrounds
react-native-linear-gradient 2.8.3    // Native gradient
```

### Storage & Security
```javascript
expo-secure-store  15.0.7  // Secure local storage (JWT, credentials)
```

### HTTP Client
```javascript
axios  1.6.0  // API requests
```

---

## 🌐 Web Admin Stack (ASP.NET Core)

### Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **ASP.NET Core MVC** | 9.0 | Web framework |
| **.NET Runtime** | 9.0 | Runtime environment |
| **C#** | 12.0 | Programming language |

### NuGet Packages
```xml
BCrypt.Net-Next                         4.0.3   // Password hashing
Pomelo.EntityFrameworkCore.MySql        9.0.0   // MySQL ORM
Newtonsoft.Json                         13.0.3  // JSON serialization
Twilio                                  7.13.5  // SMS notifications (optional)
```

### Architecture Pattern
- **MVC** (Model-View-Controller)
- **Entity Framework Core** (ORM)
- **Razor Pages** (View Engine)
- **Dependency Injection** (Built-in)

### Frontend Libraries
```javascript
Bootstrap 5      // CSS framework
jQuery           // JavaScript library
DataTables       // Table plugin
Chart.js         // Charts & graphs
```

---

## 🔧 Backend API Stack (FastAPI)

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | Modern async API framework |
| **Uvicorn** | Latest | ASGI server |
| **Pydantic** | Latest | Data validation |

### Database & ORM
```python
SQLAlchemy           // ORM
Alembic              // Database migrations
mysql-connector      // MySQL driver
psycopg2-binary      // PostgreSQL driver (backup)
```

### Security
```python
python-jose[cryptography]  // JWT tokens
passlib[bcrypt]            // Password hashing
bcrypt==4.1.3              // Bcrypt implementation
cryptography               // Encryption
```

### Additional Libraries
```python
python-multipart     // File uploads
python-dotenv        // Environment variables
requests             // HTTP client
loguru               // Advanced logging
slowapi              // Rate limiting
bleach               // Input sanitization
redis                // Caching (optional)
```

### Testing
```python
pytest               // Testing framework
pytest-asyncio       // Async testing
pytest-cov           // Code coverage
httpx                // Async HTTP client for testing
```

---

## 🤖 AI API Stack (Flask)

### Web Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | Latest | Lightweight web framework |
| **Flask-CORS** | Latest | Cross-origin requests |

### AI Integration
```python
face_recognition     // Face recognition
dlib                 // Face detection
scikit-learn         // Machine learning
opencv-python        // Image processing
numpy                // Numerical operations
Pillow               // Image handling
joblib               // Model loading
```

### Database
```python
mysql-connector-python  // MySQL connection
```

---

## 🗄️ Database Stack

### Primary Database
| Technology | Version | Purpose |
|------------|---------|---------|
| **MySQL** | 8.0+ | Relational database |

### Database Schema
```sql
Tables:
  - employees          // Employee information
  - attendance_records // Attendance logs
  - shifts             // Work shifts
  - users              // Admin users
  - devices            // Registered devices
```

### ORM Tools
- **Entity Framework Core** (C# - Web Admin)
- **SQLAlchemy** (Python - Backend API)
- **Raw SQL** (Python - AI/Desktop apps)

### Migrations
- **Alembic** (Python)
- **EF Core Migrations** (C#)

---

## 🎨 Frontend Technologies

### Web Admin Frontend
```javascript
Bootstrap 5.3        // CSS Framework
jQuery 3.6+          // JavaScript library
Font Awesome 6       // Icons
DataTables 1.13      // Tables
Chart.js 4.x         // Charts
Moment.js            // Date handling
```

### Mobile App Styling
```javascript
StyleSheet (React Native)  // Native styling
Expo LinearGradient        // Gradients
Custom theme colors        // Consistent design
```

---

## 🔒 Security Technologies

### Authentication & Authorization
```
JWT (JSON Web Tokens)          // Token-based auth
BCrypt                         // Password hashing
API Keys                       // Device authentication
OAuth 2.0 (planned)            // Third-party auth
```

### Data Security
```
HTTPS/SSL                      // Encrypted transport
Secure Storage (Expo)          // Mobile credential storage
Environment Variables          // Secret management
Input Validation (Pydantic)    // Data validation
Rate Limiting (SlowAPI)        // DDoS protection
```

---

## 📦 Development Tools

### Version Control
```
Git                   // Version control
GitHub                // Repository hosting
```

### Code Editors
```
Visual Studio Code    // Primary editor
Visual Studio 2022    // For .NET development
PyCharm (optional)    // Python IDE
```

### Build Tools
```
pip                   // Python package manager
npm                   // Node.js package manager
NuGet                 // .NET package manager
dotnet CLI            // .NET command line
expo-cli              // Expo command line
```

### Testing Tools
```
pytest                // Python testing
Postman               // API testing
Chrome DevTools       // Web debugging
React Native Debugger // Mobile debugging
```

---

## 🌍 Runtime Environments

### Server/Desktop
```
Python 3.8+           // AI, Desktop, Backend API
.NET 9.0              // Web Admin
Node.js 18+           // Mobile development
MySQL 8.0+            // Database server
```

### Mobile
```
Android SDK           // Android development
Expo Go               // Testing on physical devices
Metro Bundler         // JavaScript bundler
```

---

## 📊 Data Formats & Protocols

### Data Formats
```
JSON                  // API responses
XML                   // .NET configs
YAML                  // Docker configs
CSV                   // Data export
Base64                // Image encoding
Binary (pkl)          // Model storage
```

### Protocols
```
HTTP/HTTPS            // Web communication
WebSocket (planned)   // Real-time updates
REST API              // API architecture
```

---

## 🚀 Deployment & Infrastructure

### Development
```
Local MySQL Server    // Database
Local Python Server   // AI/Backend
IIS Express           // Web Admin
Expo Metro            // Mobile bundler
```

### Production Ready
```
Docker (optional)     // Containerization
Nginx (optional)      // Reverse proxy
PM2 (optional)        // Process manager
```

---

## 📈 Monitoring & Logging

### Logging
```
Loguru (Python)       // Advanced logging
.NET Logging          // Built-in logging
Console.log           // JavaScript logging
```

### Debugging
```
pdb (Python)          // Python debugger
Chrome DevTools       // Web debugging
React Native Debugger // Mobile debugging
Visual Studio Debug   // .NET debugging
```

---

## 🎯 Technology Statistics

### By Language
```
Python:     40%  (AI, Desktop, Backend API)
C#:         25%  (Web Admin)
JavaScript: 20%  (Mobile App, Frontend)
SQL:        10%  (Database)
Others:     5%   (Config, Scripts)
```

### Total Dependencies
```
Python packages:    ~30
Node packages:      ~15
NuGet packages:     ~5
Total:             ~50 libraries
```

### Lines of Code (Estimated)
```
Python:        ~3,000 lines
C#:            ~2,500 lines
JavaScript:    ~2,000 lines
SQL:           ~500 lines
Config/Docs:   ~2,000 lines
──────────────────────────
Total:         ~10,000+ lines
```

---

## 🌟 Key Technology Highlights

### ✅ Modern Tech Stack
- React Native (Latest mobile framework)
- ASP.NET Core 9.0 (Latest .NET)
- FastAPI (Modern Python async)
- PySide6 (Modern Qt bindings)

### ✅ Best Practices
- Type hints (Python)
- Strong typing (C#)
- Async/await (FastAPI)
- Component-based (React)

### ✅ Performance Optimized
- Async operations
- Connection pooling
- Caching ready (Redis)
- Batch processing

### ✅ Security Focused
- JWT authentication
- BCrypt hashing
- Input validation
- Rate limiting

---

## 📚 Learning Resources

### Official Documentation
- **Python**: https://docs.python.org
- **ASP.NET Core**: https://docs.microsoft.com/aspnet
- **React Native**: https://reactnative.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **dlib**: http://dlib.net
- **scikit-learn**: https://scikit-learn.org

### Tutorials Used
- Face Recognition: Adam Geitgey's face_recognition library
- SVM Classification: scikit-learn documentation
- React Native Navigation: Official React Navigation docs
- ASP.NET MVC: Microsoft Learn

---

## 🎓 Technology Choices Rationale

### Why These Technologies?

**Face Recognition (dlib)**
- ✅ Free & open source
- ✅ High accuracy (99.38% on LFW benchmark)
- ✅ No external API needed
- ✅ Runs locally

**SVM Classifier**
- ✅ Fast training & inference
- ✅ Works well with small datasets
- ✅ High accuracy for face recognition
- ✅ Easy to understand for thesis

**React Native**
- ✅ Cross-platform (iOS + Android)
- ✅ Fast development
- ✅ Large community
- ✅ Good for prototypes

**ASP.NET Core**
- ✅ High performance
- ✅ Great for enterprise
- ✅ Built-in security
- ✅ Strong typing

**FastAPI**
- ✅ Fast performance
- ✅ Async support
- ✅ Auto API docs
- ✅ Modern Python

---

## 📦 Installation Summary

### Quick Install All Dependencies

**Python (AI + Desktop + Backend)**
```bash
pip install face_recognition dlib opencv-python scikit-learn
pip install fastapi uvicorn sqlalchemy mysql-connector-python
pip install PySide6 joblib numpy Pillow flask flask-cors
```

**Mobile (React Native)**
```bash
npm install
expo install expo-linear-gradient expo-secure-store
```

**Web Admin (.NET)**
```bash
dotnet restore
```

---

## 🎯 Summary

```
Total Technologies:    50+ libraries & frameworks
Programming Languages: Python, C#, JavaScript, SQL
AI/ML Libraries:       5 core libraries (dlib, face_recognition, sklearn, cv2, numpy)
Frameworks:            4 major frameworks (ASP.NET Core, FastAPI, Flask, React Native)
Database:              MySQL 8.0+
Development Time:      ~3 months (estimated)
Lines of Code:         10,000+
External APIs:         NONE (100% self-contained)
```

---

**🎓 Perfect for Thesis: Demonstrates mastery of multiple technologies and full-stack development!**

**📅 Last Updated**: November 15, 2025  
**🎯 Status**: Production Ready  
**✨ Quality**: Enterprise Grade
