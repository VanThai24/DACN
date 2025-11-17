"""
Test script cho Anti-Spoofing và Mask Detection
Chạy: python test_security.py
"""

import requests
import base64
import sys
import os

# API URL
API_URL = "http://localhost:5000"

def test_anti_spoofing(image_path):
    """Test anti-spoofing detection"""
    print(f"\n🔒 Testing Anti-Spoofing với: {image_path}")
    
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    
    # Gửi request
    files = {'image': img_bytes}
    response = requests.post(f"{API_URL}/security/anti-spoofing", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Kết quả: {result['message']}")
        print(f"  - Is Real: {result['is_real']}")
        print(f"  - Confidence: {result['confidence']:.2%}")
        print(f"  - Scores:")
        for key, value in result['scores'].items():
            print(f"    • {key}: {value:.3f}")
        return result
    else:
        print(f"✗ Lỗi: {response.text}")
        return None


def test_mask_detection(image_path):
    """Test mask detection"""
    print(f"\n😷 Testing Mask Detection với: {image_path}")
    
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    
    # Gửi request
    files = {'image': img_bytes}
    response = requests.post(f"{API_URL}/security/mask-detection", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Kết quả: {result['message']}")
        print(f"  - Wearing Mask: {result['wearing_mask']}")
        print(f"  - Confidence: {result['confidence']:.2%}")
        if 'scores' in result:
            print(f"  - Scores:")
            for key, value in result['scores'].items():
                print(f"    • {key}: {value:.3f}")
        return result
    else:
        print(f"✗ Lỗi: {response.text}")
        return None


def test_full_scan(image_path):
    """Test full scan (recognition + anti-spoofing + mask detection)"""
    print(f"\n🎯 Testing Full Scan với: {image_path}")
    
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    
    # Gửi request
    files = {'image': img_bytes}
    response = requests.post(f"{API_URL}/scan", files=files)
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    if result.get('success'):
        print(f"✓ Điểm danh thành công!")
        print(f"  - Name: {result['name']}")
        print(f"  - Confidence: {result['confidence']:.2%}")
        print(f"  - Security:")
        print(f"    • Anti-spoofing passed: {result['security']['anti_spoofing']['passed']}")
        print(f"    • Mask detection passed: {result['security']['mask_detection']['passed']}")
    else:
        print(f"✗ Điểm danh thất bại!")
        print(f"  - Reason: {result.get('reason', 'Unknown')}")
        print(f"  - Message: {result.get('message', 'No message')}")
    
    return result


def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 SECURITY MODULE TEST SUITE")
    print("=" * 60)
    
    # Kiểm tra server đang chạy
    try:
        response = requests.get(API_URL)
        print(f"✓ Server is running: {response.json()['status']}")
    except:
        print("✗ Server is not running! Start server first: python app.py")
        sys.exit(1)
    
    # Test với ảnh mẫu
    test_images = {
        'real_face': 'face_data/Thai/Thai_1.jpg',  # Thay đổi path tùy project
        'printed_photo': 'test_images/printed_photo.jpg',
        'with_mask': 'test_images/with_mask.jpg',
        'without_mask': 'test_images/without_mask.jpg'
    }
    
    # Test Anti-Spoofing
    print("\n" + "=" * 60)
    print("PART 1: ANTI-SPOOFING DETECTION")
    print("=" * 60)
    
    for name, path in test_images.items():
        if os.path.exists(path):
            test_anti_spoofing(path)
        else:
            print(f"\n⚠ Bỏ qua {name}: File không tồn tại ({path})")
    
    # Test Mask Detection
    print("\n" + "=" * 60)
    print("PART 2: MASK DETECTION")
    print("=" * 60)
    
    for name, path in test_images.items():
        if os.path.exists(path):
            test_mask_detection(path)
        else:
            print(f"\n⚠ Bỏ qua {name}: File không tồn tại ({path})")
    
    # Test Full Scan
    print("\n" + "=" * 60)
    print("PART 3: FULL SCAN (Recognition + Security)")
    print("=" * 60)
    
    # Test với ảnh thật
    real_face_path = 'face_data/Thai/Thai_1.jpg'
    if os.path.exists(real_face_path):
        test_full_scan(real_face_path)
    else:
        print(f"\n⚠ File không tồn tại: {real_face_path}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
