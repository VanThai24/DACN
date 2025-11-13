# Quick test Flask server
import pickle
import os

MODEL_PATH = 'D:/DACN/DACN/AI/faceid_best_model.pkl'

print(f"Testing: {MODEL_PATH}")
print(f"Exists: {os.path.exists(MODEL_PATH)}")
print(f"Size: {os.path.getsize(MODEL_PATH)} bytes")

try:
    with open(MODEL_PATH, 'rb') as f:
        clf = pickle.load(f)
    print("✅ Model loaded OK!")
    print(f"Type: {type(clf)}")
except Exception as e:
    print(f"❌ Error: {e}")
