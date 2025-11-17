"""
Anti-Spoofing Detection Module
Phát hiện giả mạo bằng ảnh/video sử dụng texture analysis và liveness detection
"""

import cv2
import numpy as np
from PIL import Image
import io

class AntiSpoofing:
    """
    Anti-spoofing detector sử dụng nhiều phương pháp:
    1. Texture Analysis - Phân tích texture để phát hiện ảnh in/màn hình
    2. Color Diversity - Kiểm tra độ đa dạng màu sắc
    3. Face Quality - Kiểm tra chất lượng khuôn mặt
    4. Moiré Pattern Detection - Phát hiện pattern từ màn hình
    """
    
    def __init__(self, threshold=0.7):
        """
        Args:
            threshold: Ngưỡng để phân loại real/fake (0-1)
        """
        self.threshold = threshold
    
    def analyze_texture(self, img_array):
        """
        Phân tích texture sử dụng Local Binary Pattern (LBP)
        Ảnh thật có texture phức tạp hơn ảnh in/màn hình
        """
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Tính độ biến thiên cục bộ
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize về 0-1
        texture_score = min(laplacian_var / 100.0, 1.0)
        
        return texture_score
    
    def analyze_color_diversity(self, img_array):
        """
        Phân tích độ đa dạng màu sắc
        Ảnh thật có phân bố màu tự nhiên hơn
        """
        # Chuyển sang HSV
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Tính histogram cho Hue channel
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist = hist.flatten() / hist.sum()
        
        # Tính entropy (độ đa dạng)
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        
        # Normalize về 0-1
        color_score = min(entropy / 8.0, 1.0)
        
        return color_score
    
    def detect_moire_pattern(self, img_array):
        """
        Phát hiện Moiré pattern (vân sóng từ màn hình)
        """
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply FFT để phát hiện periodic patterns
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # Tính tỉ lệ high frequency
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        
        # Loại bỏ DC component
        magnitude[center_h-10:center_h+10, center_w-10:center_w+10] = 0
        
        # Tính tỉ lệ high frequency energy
        high_freq = magnitude[0:h//4, :].sum() + magnitude[3*h//4:, :].sum()
        total_freq = magnitude.sum()
        
        high_freq_ratio = high_freq / (total_freq + 1e-7)
        
        # Moiré pattern có high frequency cao
        moire_score = 1.0 - min(high_freq_ratio * 10, 1.0)
        
        return moire_score
    
    def check_face_quality(self, img_array):
        """
        Kiểm tra chất lượng khuôn mặt (sharpness, lighting)
        """
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Kiểm tra sharpness
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(sharpness / 100.0, 1.0)
        
        # Kiểm tra contrast
        contrast = gray.std()
        contrast_score = min(contrast / 50.0, 1.0)
        
        # Kiểm tra brightness
        brightness = gray.mean()
        brightness_score = 1.0 - abs(brightness - 127) / 127.0
        
        quality_score = (sharpness_score + contrast_score + brightness_score) / 3.0
        
        return quality_score
    
    def detect(self, img_bytes):
        """
        Phát hiện spoofing attack
        
        Args:
            img_bytes: Ảnh dưới dạng bytes
            
        Returns:
            dict: {
                'is_real': bool,
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
            
            # Tính các scores
            texture_score = self.analyze_texture(img_array)
            color_score = self.analyze_color_diversity(img_array)
            moire_score = self.detect_moire_pattern(img_array)
            quality_score = self.check_face_quality(img_array)
            
            # Weighted average
            weights = {
                'texture': 0.3,
                'color': 0.2,
                'moire': 0.3,
                'quality': 0.2
            }
            
            confidence = (
                texture_score * weights['texture'] +
                color_score * weights['color'] +
                moire_score * weights['moire'] +
                quality_score * weights['quality']
            )
            
            is_real = confidence >= self.threshold
            
            return {
                'is_real': bool(is_real),
                'confidence': float(confidence),
                'scores': {
                    'texture': float(texture_score),
                    'color_diversity': float(color_score),
                    'moire_pattern': float(moire_score),
                    'face_quality': float(quality_score)
                },
                'message': 'Real face detected' if is_real else 'Spoofing attack detected'
            }
            
        except Exception as e:
            return {
                'is_real': False,
                'confidence': 0.0,
                'error': str(e),
                'message': 'Error during anti-spoofing detection'
            }


# Test code
if __name__ == "__main__":
    detector = AntiSpoofing(threshold=0.7)
    
    # Test với ảnh mẫu
    with open("test_image.jpg", "rb") as f:
        img_bytes = f.read()
        result = detector.detect(img_bytes)
        print(f"Result: {result}")
