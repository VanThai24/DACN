-- =============================================
-- Migration: Add Overtime Columns to Shifts Table
-- Date: 2025-11-17
-- Description: Thêm cột IsOvertime và OvertimeNote 
--              để admin có thể đánh dấu và ghi chú ca tăng ca
-- =============================================

USE attendance_db;

-- Thêm cột is_overtime (boolean, mặc định FALSE)
ALTER TABLE shifts 
ADD COLUMN is_overtime BOOLEAN DEFAULT FALSE NOT NULL
COMMENT 'Đánh dấu có phải ca tăng ca không';

-- Thêm cột overtime_note (text, nullable)
ALTER TABLE shifts 
ADD COLUMN overtime_note VARCHAR(500) NULL
COMMENT 'Ghi chú về ca tăng ca (lý do, yêu cầu đặc biệt, v.v.)';

-- Tạo index để tìm kiếm nhanh các ca tăng ca
CREATE INDEX idx_shifts_overtime ON shifts(is_overtime, date);

-- Xem kết quả
DESCRIBE shifts;

-- =============================================
-- Test Queries
-- =============================================

-- Tìm tất cả ca tăng ca
-- SELECT * FROM shifts WHERE is_overtime = TRUE;

-- Đếm số ca tăng ca theo nhân viên
-- SELECT e.name, COUNT(*) as overtime_count 
-- FROM shifts s
-- JOIN employees e ON s.employee_id = e.id
-- WHERE s.is_overtime = TRUE
-- GROUP BY e.name;

-- Ca tăng ca trong tháng này
-- SELECT s.*, e.name 
-- FROM shifts s
-- JOIN employees e ON s.employee_id = e.id
-- WHERE s.is_overtime = TRUE 
-- AND MONTH(s.date) = MONTH(CURRENT_DATE())
-- AND YEAR(s.date) = YEAR(CURRENT_DATE());

-- =============================================
-- Rollback (nếu cần)
-- =============================================
-- ALTER TABLE shifts DROP COLUMN is_overtime;
-- ALTER TABLE shifts DROP COLUMN overtime_note;
-- DROP INDEX idx_shifts_overtime ON shifts;
