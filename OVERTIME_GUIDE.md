# ⏰ TĂNG CA - Hướng Dẫn Thêm Tính Năng

## 📊 Tình Trạng Hiện Tại

### ⚠️ Hạn Chế Hiện Tại
```
❌ Chỉ hỗ trợ 2 ca cố định:
   - Ca Sáng: 06:00 - 12:30 (làm 08:30-11:30)
   - Ca Chiều: 12:30 - 16:30 (làm 13:30-16:30)

❌ Không cho phép điểm danh sau 16:30
❌ Không có ca tăng ca/ca đêm
❌ Không linh hoạt về thời gian
```

### 🎯 Cần Bổ Sung
```
✅ Ca Tăng Ca: 16:30 - 20:00
✅ Ca Đêm: 20:00 - 02:00 (ngày hôm sau)
✅ Ca Cuối Tuần: Thời gian linh hoạt
✅ Overtime tracking: Tính giờ làm thêm
```

---

## 🔧 Cách Thêm Tính Năng Tăng Ca

### 1️⃣ **Cập Nhật Database Schema**

#### Bảng `shifts` (Đã có - OK)
```sql
-- Bảng shifts hiện tại đã đủ, không cần thay đổi
CREATE TABLE shifts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    date DATETIME NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

#### Thêm Bảng `overtime` (Mới)
```sql
CREATE TABLE overtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    overtime_hours DECIMAL(4,2) NOT NULL, -- Số giờ tăng ca
    shift_type ENUM('evening', 'night', 'weekend') NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

---

### 2️⃣ **Cập Nhật Logic Phát Hiện Ca**

#### File: `faceid_desktop/main.py`
**Thay thế code hiện tại:**

```python
# 🔥 TỰ ĐỘNG XÁC ĐỊNH CA LÀM VIỆC - PHIÊN BẢN MỚI
def determine_shift(current_time, current_date):
    """
    Xác định ca làm việc dựa trên thời gian điểm danh
    Hỗ trợ: Ca Sáng, Ca Chiều, Ca Tăng Ca, Ca Đêm
    """
    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
    
    # Ca Sáng: 06:00 - 12:30
    if time(6, 0) <= current_time < time(12, 30):
        return {
            'start_time': time(8, 30),
            'end_time': time(11, 30),
            'name': "Ca Sáng",
            'type': 'regular',
            'overtime_rate': 1.0
        }
    
    # Ca Chiều: 12:30 - 16:30  
    elif time(12, 30) <= current_time < time(16, 30):
        return {
            'start_time': time(13, 30),
            'end_time': time(16, 30),
            'name': "Ca Chiều", 
            'type': 'regular',
            'overtime_rate': 1.0
        }
    
    # ✨ CA TĂNG CA: 16:30 - 20:00
    elif time(16, 30) <= current_time < time(20, 0):
        return {
            'start_time': time(16, 30),
            'end_time': time(20, 0),
            'name': "Ca Tăng Ca",
            'type': 'overtime',
            'overtime_rate': 1.5  # x1.5 lương
        }
    
    # ✨ CA ĐÊM: 20:00 - 02:00 (ngày hôm sau)
    elif current_time >= time(20, 0) or current_time < time(2, 0):
        # Xử lý đặc biệt cho ca đêm qua ngày
        if current_time >= time(20, 0):
            shift_date = current_date
        else:
            shift_date = current_date - timedelta(days=1)
            
        return {
            'start_time': time(20, 0),
            'end_time': time(2, 0),
            'name': "Ca Đêm",
            'type': 'night',
            'overtime_rate': 2.0,  # x2 lương
            'shift_date': shift_date
        }
    
    # ✨ CUỐI TUẦN: Tất cả giờ đều là tăng ca
    elif weekday in [5, 6]:  # Saturday, Sunday
        if time(6, 0) <= current_time < time(18, 0):
            return {
                'start_time': time(8, 0),
                'end_time': time(17, 0),
                'name': "Ca Cuối Tuần",
                'type': 'weekend',
                'overtime_rate': 2.0
            }
    
    # Ngoài giờ làm việc
    else:
        return {
            'name': "Ngoài Giờ",
            'type': 'invalid',
            'message': "Không trong khung giờ làm việc"
        }

# Thay thế logic cũ
shift_info = determine_shift(current_time, current_date)

if shift_info['type'] == 'invalid':
    # Hiển thị thông báo ngoài giờ
    self.label.setText(f"⏰ {shift_info['message']}")
    return

# Tiếp tục xử lý như cũ với shift_info
```

---

### 3️⃣ **Cập Nhật AI API (Flask)**

#### File: `AI/app.py`
```python
def determine_shift_api(current_time, current_date):
    """API version - tương tự như desktop app"""
    # Copy logic từ trên
    pass

@app.route('/recognize', methods=['POST'])
def recognize():
    # Existing code...
    
    # Thay thế logic xác định ca
    shift_info = determine_shift_api(current_time, current_date)
    
    if shift_info['type'] == 'invalid':
        return jsonify({
            'success': False,
            'error': shift_info['message'],
            'current_time': current_time.strftime('%H:%M')
        })
    
    # Lưu thông tin overtime nếu cần
    if shift_info['type'] in ['overtime', 'night', 'weekend']:
        save_overtime_record(employee_id, current_date, shift_info)
    
    # Continue with existing logic...
```

---

### 4️⃣ **Cập Nhật Web Admin**

#### Model: `Models/Overtime.cs`
```csharp
[Table("overtime")]
public class Overtime
{
    [Key]
    public int Id { get; set; }
    
    [Column("employee_id")]
    public int EmployeeId { get; set; }
    
    public DateTime Date { get; set; }
    
    [Column("overtime_hours")]
    public decimal OvertimeHours { get; set; }
    
    [Column("shift_type")]
    public string ShiftType { get; set; } // "evening", "night", "weekend"
    
    public bool Approved { get; set; }
    
    [Column("created_at")]
    public DateTime CreatedAt { get; set; }
    
    // Navigation property
    public virtual Employee Employee { get; set; }
}
```

#### Controller: `Controllers/OvertimeController.cs`
```csharp
public class OvertimeController : BaseAdminController
{
    public IActionResult Index()
    {
        var overtimes = _context.Overtimes
            .Include(o => o.Employee)
            .OrderByDescending(o => o.Date)
            .ToList();
        return View(overtimes);
    }
    
    [HttpPost]
    public IActionResult Approve(int id)
    {
        var overtime = _context.Overtimes.Find(id);
        if (overtime != null)
        {
            overtime.Approved = true;
            _context.SaveChanges();
        }
        return RedirectToAction("Index");
    }
    
    public IActionResult Report()
    {
        // Báo cáo tăng ca theo tháng
        var report = _context.Overtimes
            .Where(o => o.Date.Month == DateTime.Now.Month)
            .GroupBy(o => o.Employee.Name)
            .Select(g => new {
                Employee = g.Key,
                TotalHours = g.Sum(o => o.OvertimeHours),
                TotalSessions = g.Count()
            })
            .ToList();
        
        return View(report);
    }
}
```

#### View: `Views/Overtime/Index.cshtml`
```html
<div class="card">
    <div class="card-header">
        <h3>Quản Lý Tăng Ca</h3>
    </div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Nhân Viên</th>
                    <th>Ngày</th>
                    <th>Loại Ca</th>
                    <th>Số Giờ</th>
                    <th>Trạng Thái</th>
                    <th>Hành Động</th>
                </tr>
            </thead>
            <tbody>
                @foreach(var item in Model)
                {
                    <tr>
                        <td>@item.Employee.Name</td>
                        <td>@item.Date.ToString("dd/MM/yyyy")</td>
                        <td>
                            @switch(item.ShiftType)
                            {
                                case "evening": <span class="badge bg-warning">Tăng Ca</span> break;
                                case "night": <span class="badge bg-dark">Ca Đêm</span> break;  
                                case "weekend": <span class="badge bg-info">Cuối Tuần</span> break;
                            }
                        </td>
                        <td>@item.OvertimeHours giờ</td>
                        <td>
                            @if(item.Approved)
                            {
                                <span class="badge bg-success">Đã Duyệt</span>
                            }
                            else
                            {
                                <span class="badge bg-secondary">Chờ Duyệt</span>
                            }
                        </td>
                        <td>
                            @if(!item.Approved)
                            {
                                <form asp-action="Approve" method="post" style="display:inline">
                                    <input type="hidden" name="id" value="@item.Id" />
                                    <button type="submit" class="btn btn-sm btn-success">Duyệt</button>
                                </form>
                            }
                        </td>
                    </tr>
                }
            </tbody>
        </table>
    </div>
</div>
```

---

### 5️⃣ **Cập Nhật Mobile App**

#### File: `mobile_app/screens/AttendanceScreen.js`
```javascript
// Thêm hiển thị overtime
const getShiftDisplay = (record) => {
    if (!record.shift_type) return "Ca Thường";
    
    switch(record.shift_type) {
        case 'overtime': return "🌆 Tăng Ca";
        case 'night': return "🌙 Ca Đêm"; 
        case 'weekend': return "📅 Cuối Tuần";
        default: return "Ca Thường";
    }
};

// Thêm stats overtime
const calculateOvertimeStats = (records) => {
    const overtimeRecords = records.filter(r => 
        ['overtime', 'night', 'weekend'].includes(r.shift_type)
    );
    
    return {
        totalOvertimeHours: overtimeRecords.length * 3.5, // Estimate
        overtimeSessions: overtimeRecords.length,
        overtimePay: overtimeRecords.length * 3.5 * 50000 // Estimate
    };
};

// Cập nhật UI stats cards
<View style={styles.statsGrid}>
    <StatsCard 
        title="Tăng Ca"
        value={`${overtimeStats.overtimeSessions} ca`}
        color="#ff9800"
        icon="⏰"
    />
    <StatsCard 
        title="Giờ TC"
        value={`${overtimeStats.totalOvertimeHours}h`}
        color="#9c27b0"
        icon="🕐"
    />
</View>
```

---

## 📋 Implementation Steps

### Bước 1: Cập Nhật Database
```sql
-- Chạy trên MySQL
CREATE TABLE overtime (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    overtime_hours DECIMAL(4,2) NOT NULL,
    shift_type ENUM('evening', 'night', 'weekend') NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

### Bước 2: Test Thời Gian
```python
# Test script
from datetime import datetime, time

def test_shift_detection():
    test_times = [
        time(7, 0),   # Ca sáng
        time(14, 0),  # Ca chiều
        time(17, 0),  # Tăng ca ✨
        time(21, 0),  # Ca đêm ✨
        time(1, 0),   # Ca đêm (ngày hôm sau) ✨
        time(3, 0),   # Ngoài giờ
    ]
    
    for t in test_times:
        result = determine_shift(t, datetime.now().date())
        print(f"{t} → {result['name']} ({result['type']})")

test_shift_detection()
```

### Bước 3: Deploy Changes
```bash
# 1. Backup database
mysqldump -u root -p12345 attendance_db > backup.sql

# 2. Update database schema
mysql -u root -p12345 attendance_db < overtime_schema.sql

# 3. Update Python files
# Copy new code to faceid_desktop/main.py and AI/app.py

# 4. Update Web Admin
cd DACN && dotnet build && dotnet run

# 5. Test
python test_shift_detection.py
```

---

## 📊 Expected Results

### ✅ Sau Khi Thêm Tính Năng

#### Desktop App
```
✅ Cho phép điểm danh 24/7
✅ Tự động phát hiện 4 loại ca:
   - Ca Sáng (06:00-12:30)
   - Ca Chiều (12:30-16:30)  
   - Ca Tăng Ca (16:30-20:00) ✨
   - Ca Đêm (20:00-02:00) ✨
   - Ca Cuối Tuần ✨
✅ Hiển thị hệ số lương (x1.5, x2)
```

#### Web Admin
```
✅ Trang quản lý tăng ca mới
✅ Duyệt/từ chối tăng ca
✅ Báo cáo tăng ca theo tháng
✅ Tính toán giờ làm thêm
```

#### Mobile App
```
✅ Hiển thị icon phân biệt ca thường/tăng ca
✅ Stats tăng ca trong tháng
✅ Ước tính thu nhập tăng ca
```

---

## 🎯 Demo Scenarios

### Scenario 1: Nhân Viên Tăng Ca
```
17:00 - Điểm danh tăng ca
→ "🌆 TĂNG CA - 16:30-20:00"
→ "Hệ số lương: x1.5"
→ Lưu vào bảng overtime
```

### Scenario 2: Ca Đêm
```
21:00 - Điểm danh ca đêm
→ "🌙 CA ĐÊM - 20:00-02:00"
→ "Hệ số lương: x2.0"
→ "Ngày: 15/11/2025" (đúng ngày bắt đầu)
```

### Scenario 3: Cuối Tuần
```
09:00 Thứ 7 - Điểm danh
→ "📅 CA CUỐI TUẦN - 08:00-17:00"
→ "Hệ số lương: x2.0"
→ "Toàn bộ ca đều là tăng ca"
```

---

## 💡 Advanced Features (Optional)

### 1. Flexible Overtime Rules
```python
# Config file for overtime rules
OVERTIME_RULES = {
    'max_hours_per_day': 4,
    'max_hours_per_week': 20,
    'rates': {
        'evening': 1.5,
        'night': 2.0,
        'weekend': 2.0,
        'holiday': 3.0
    }
}
```

### 2. Manager Approval Workflow
```python
# Email notification when overtime recorded
def send_overtime_notification(employee_id, hours):
    manager_email = get_manager_email(employee_id)
    send_email(
        to=manager_email,
        subject=f"Tăng ca cần duyệt - {employee_name}",
        body=f"Nhân viên làm tăng ca {hours} giờ..."
    )
```

### 3. Auto Calculate Salary
```python
def calculate_overtime_pay(employee_id, month):
    overtime_records = get_overtime_records(employee_id, month)
    base_hourly_rate = get_base_rate(employee_id)
    
    total_pay = 0
    for record in overtime_records:
        if record.approved:
            rate_multiplier = OVERTIME_RULES['rates'][record.shift_type]
            pay = record.overtime_hours * base_hourly_rate * rate_multiplier
            total_pay += pay
    
    return total_pay
```

---

## 🚀 Quick Implementation (Minimal)

### Chỉ Muốn Thêm Ca Tăng Ca Nhanh (10 phút)

#### Bước 1: Cập nhật `faceid_desktop/main.py`
```python
# Thay dòng 468-475 bằng:
if time(6, 0) <= current_time < time(12, 30):
    shift_start = time(8, 30)
    shift_end = time(11, 30)
    shift_name = "Ca Sáng"
elif time(12, 30) <= current_time < time(16, 30):
    shift_start = time(13, 30) 
    shift_end = time(16, 30)
    shift_name = "Ca Chiều"
elif time(16, 30) <= current_time < time(20, 0):  # ✨ MỚI
    shift_start = time(16, 30)
    shift_end = time(20, 0) 
    shift_name = "🌆 Tăng Ca"
else:
    # Cho phép ca đêm
    shift_start = time(20, 0)
    shift_end = time(23, 59)
    shift_name = "🌙 Ca Đêm"

# Xóa check time > 16:30 (dòng 443-462)
```

#### Bước 2: Test
```bash
cd faceid_desktop
python main.py
# Test vào lúc 17:00, 21:00
```

**Kết quả:** Hệ thống cho phép điểm danh tăng ca ngay! ✅

---

**🎯 Tóm tắt: Hệ thống hiện tại chưa hỗ trợ tăng ca, nhưng có thể bổ sung dễ dàng bằng cách mở rộng logic xác định ca và thêm bảng overtime để tracking.**

**📅 Thời gian implement: 30 phút (minimal) đến 2-3 giờ (full featured)**