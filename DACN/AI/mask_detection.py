"""
Mask Detection Module
Phát hiện người đeo khẩu trang sử dụng face landmarks và color analysis
"""

import cv2
import numpy as np
from PIL import Image
import io
import face_recognition

class MaskDetector:
    """
    Mask detector sử dụng face landmarks để phát hiện khẩu trang
    Phương pháp:
    1. Phát hiện face landmarks (nose, mouth, chin)
    2. Phân tích vùng mũi-miệng-cằm
    3. Kiểm tra texture và màu sắc
    """
    
    def __init__(self, threshold=0.6):
        """
        Args:
            threshold: Ngưỡng để phân loại có/không đeo khẩu trang (0-1)
        """
        self.threshold = threshold
    
    def get_face_landmarks(self, img_array):
        """
        Lấy face landmarks sử dụng face_recognition
        """
        # Detect face locations
        face_locations = face_recognition.face_locations(img_array)
        
        if len(face_locations) == 0:
            return None, None
        
        # Get landmarks for first face
        face_landmarks = face_recognition.face_landmarks(img_array, face_locations)
        
        if len(face_landmarks) == 0:
            return None, None
        
        return face_locations[0], face_landmarks[0]
    
    def extract_mouth_nose_region(self, img_array, landmarks):
        """
        Trích xuất vùng mũi-miệng từ landmarks
        """
        if landmarks is None:
            return None
        
        # Lấy các điểm quan trọng
        nose_points = landmarks.get('nose_bridge', []) + landmarks.get('nose_tip', [])
        mouth_points = landmarks.get('top_lip', []) + landmarks.get('bottom_lip', [])
        chin_points = landmarks.get('chin', [])
        
        if not nose_points or not mouth_points:
            return None
        
        # Tạo mask cho vùng nose-mouth
        mask = np.zeros(img_array.shape[:2], dtype=np.uint8)
        
        all_points = nose_points + mouth_points
        if chin_points:
            # Chỉ lấy một số điểm chin ở giữa
            mid_idx = len(chin_points) // 2
            all_points += chin_points[mid_idx-2:mid_idx+3]
        
        points = np.array(all_points, dtype=np.int32)
        cv2.fillConvexPoly(mask, points, 255)
        
        # Extract region
        region = cv2.bitwise_and(img_array, img_array, mask=mask)
        
        return region, mask
    
    def analyze_region_visibility(self, region, mask):
        """
        Phân tích độ rõ ràng của vùng nose-mouth
        Nếu đeo khẩu trang, vùng này sẽ bị che và có texture/màu đồng nhất
        """
        # Chỉ lấy vùng có mask
        masked_pixels = region[mask > 0]
        
        if len(masked_pixels) == 0:
            return 0.5
        
        # Tính độ biến thiên màu sắc
        std_dev = np.std(masked_pixels, axis=0).mean()
        
        # Normalize (std cao = không đeo khẩu trang)
        visibility_score = min(std_dev / 30.0, 1.0)
        
        return visibility_score
    
    def detect_uniform_color(self, region, mask):
        """
        Phát hiện màu đồng nhất (đặc trưng của khẩu trang)
        """
        masked_pixels = region[mask > 0]
        
        if len(masked_pixels) == 0:
            return 0.5
        
        # Tính dominant color
        mean_color = masked_pixels.mean(axis=0)
        
        # Tính khoảng cách từ mỗi pixel đến mean color
        distances = np.linalg.norm(masked_pixels - mean_color, axis=1)
        mean_distance = distances.mean()
        
        # Màu đồng nhất = distance nhỏ
        uniformity_score = 1.0 - min(mean_distance / 50.0, 1.0)
        
        return uniformity_score
    
    def detect_texture_pattern(self, region, mask):
        """
        Phát hiện texture pattern của vải khẩu trang
        """
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
        
        # Calculate texture using gradient
        grad_x = cv2.Sobel(masked_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(masked_gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # Mask gradient
        masked_gradient = gradient_mag[mask > 0]
        
        if len(masked_gradient) == 0:
            return 0.5
        
        # Texture thấp = có thể là khẩu trang
        avg_gradient = masked_gradient.mean()
        texture_score = 1.0 - min(avg_gradient / 20.0, 1.0)
        
        return texture_score
    
    def detect(self, img_bytes):
        """
        Phát hiện người đeo khẩu trang
        
        Args:
            img_bytes: Ảnh dưới dạng bytes
            
        Returns:
            dict: {
                'wearing_mask': bool,
                'confidence': float (0-1),
                'scores': dict với các scores chi tiết
            }
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(img_bytes))
            img_array = np.array(img)
            
            # Ensure RGB
            if len(img_array.shape) == 2:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            
            # Get face landmarks
            face_location, landmarks = self.get_face_landmarks(img_array)
            
            if landmarks is None:
                return {
                    'wearing_mask': False,
                    'confidence': 0.0,
                    'message': 'No face detected',
                    'scores': {}
                }
            
            # Extract nose-mouth region
            result = self.extract_mouth_nose_region(img_array, landmarks)
            if result is None:
                return {
                    'wearing_mask': False,
                    'confidence': 0.0,
                    'message': 'Could not extract face region',
                    'scores': {}
                }
            
            region, mask = result
            
            # Analyze region
            visibility_score = self.analyze_region_visibility(region, mask)
            uniformity_score = self.detect_uniform_color(region, mask)
            texture_score = self.detect_texture_pattern(region, mask)
            
            # Weighted average (đảo ngược visibility vì visibility thấp = đeo khẩu trang)
            weights = {
                'visibility': 0.4,  # Độ rõ thấp
                'uniformity': 0.3,  # Màu đồng nhất
                'texture': 0.3      # Texture vải
            }
            
            mask_confidence = (
                (1.0 - visibility_score) * weights['visibility'] +
                uniformity_score * weights['uniformity'] +
                texture_score * weights['texture']
            )
            
            wearing_mask = mask_confidence >= self.threshold
            
            return {
                'wearing_mask': bool(wearing_mask),
                'confidence': float(mask_confidence),
                'scores': {
                    'visibility': float(visibility_score),
                    'uniformity': float(uniformity_score),
                    'texture': float(texture_score)
                },
                'message': 'Wearing mask' if wearing_mask else 'Not wearing mask',
                'face_detected': True
            }
            
        except Exception as e:
            return {
                'wearing_mask': False,
                'confidence': 0.0,
                'error': str(e),
                'message': 'Error during mask detection',
                'face_detected': False
            }


# Test code
if __name__ == "__main__":
    detector = MaskDetector(threshold=0.6)
    
    # Test với ảnh mẫu
    with open("test_image.jpg", "rb") as f:
        img_bytes = f.read()
        result = detector.detect(img_bytes)
        print(f"Result: {result}")
