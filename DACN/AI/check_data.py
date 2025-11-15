"""
Kiểm tra nhanh dữ liệu training
Hiển thị số lượng ảnh mỗi người và đưa ra khuyến nghị
"""

import os
from glob import glob
from pathlib import Path

def check_training_data():
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'face_data'
    
    if not data_dir.exists():
        print(f"❌ Thư mục {data_dir} không tồn tại!")
        return
    
    print("\n" + "="*70)
    print("📊 KIỂM TRA DỮ LIỆU TRAINING")
    print("="*70)
    
    people = sorted([d for d in data_dir.iterdir() if d.is_dir()])
    
    if not people:
        print("❌ Không tìm thấy thư mục nào trong face_data!")
        print("\n💡 Hướng dẫn:")
        print("   1. Chạy: python capture_training_data.py")
        print("   2. Hoặc tạo thư mục thủ công: face_data/[Tên người]/")
        return
    
    total_images = 0
    data_summary = []
    
    for person_dir in people:
        images = list(person_dir.glob('*.jpg')) + \
                list(person_dir.glob('*.jpeg')) + \
                list(person_dir.glob('*.png'))
        
        count = len(images)
        total_images += count
        
        # Đánh giá
        if count >= 40:
            status = "✅ Tốt"
            color = "🟢"
        elif count >= 20:
            status = "⚠️  Khá"
            color = "🟡"
        else:
            status = "❌ Thiếu"
            color = "🔴"
        
        data_summary.append({
            'name': person_dir.name,
            'count': count,
            'status': status,
            'color': color
        })
    
    # Hiển thị bảng
    print(f"\n{'Tên':<15} {'Số ảnh':>10} {'Trạng thái':>12}")
    print("-" * 70)
    
    for item in data_summary:
        print(f"{item['name']:<15} {item['count']:>10} {item['color']} {item['status']:>10}")
    
    print("-" * 70)
    print(f"{'TỔNG CỘNG':<15} {total_images:>10}")
    print("="*70)
    
    # Đưa ra khuyến nghị
    print("\n📋 ĐÁNH GIÁ & KHUYẾN NGHỊ:")
    print("-" * 70)
    
    avg_images = total_images / len(people) if people else 0
    
    if avg_images >= 40:
        print("✅ Dữ liệu TỐT! Có thể train model ngay.")
        print("   → Chạy: python train_best_model.py")
    elif avg_images >= 20:
        print("⚠️  Dữ liệu KHÁ. Nên thu thập thêm để tăng độ chính xác.")
        print("   → Mục tiêu: 40-50 ảnh/người")
        print("   → Chạy: python capture_training_data.py")
    else:
        print("❌ Dữ liệu THIẾU! Cần thu thập nhiều hơn.")
        print("   → Yêu cầu tối thiểu: 30 ảnh/người")
        print("   → Khuyến nghị: 40-50 ảnh/người")
        print("   → Chạy: python capture_training_data.py")
    
    # Kiểm tra balance
    counts = [item['count'] for item in data_summary]
    max_count = max(counts)
    min_count = min(counts)
    
    if max_count / min_count > 2:
        print("\n⚠️  CẢNH BÁO: Dữ liệu không cân bằng!")
        print(f"   Chênh lệch: {min_count} - {max_count} ảnh")
        print("   → Nên thu thập thêm cho người có ít ảnh nhất")
    
    # Danh sách người cần thu thập thêm
    need_more = [item for item in data_summary if item['count'] < 30]
    if need_more:
        print("\n🎯 NGƯỜI CẦN THU THẬP THÊM:")
        for item in need_more:
            needed = 40 - item['count']
            print(f"   - {item['name']}: Cần thêm ~{needed} ảnh")
    
    print("\n" + "="*70)
    print("💡 GỢI Ý TIẾP THEO:")
    print("-" * 70)
    
    if avg_images >= 30:
        print("1. ✅ Train model: python train_best_model.py")
        print("2. ✅ Update embeddings: python update_embeddings_best_model.py")
        print("3. ✅ Test hệ thống: cd ../faceid_desktop && python main.py")
    else:
        print("1. 📸 Thu thập thêm dữ liệu: python capture_training_data.py")
        print("2. 📊 Kiểm tra lại: python check_data.py")
        print("3. 🔄 Train model: python train_best_model.py")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    check_training_data()
