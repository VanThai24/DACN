using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

using System.ComponentModel.DataAnnotations.Schema;
namespace Models
{
    [Table("attendance_records")]
    public class AttendanceRecord
    {
        [Key]
        public int Id { get; set; }
    [Column("employee_id")]
    public int EmployeeId { get; set; }
    [Column("timestamp_in")]
    public DateTime? TimestampIn { get; set; }
    // Đã xóa cột timestamp_out khỏi database, loại bỏ property này
    public string? Status { get; set; }
    [Column("photo_path")]
    public string? PhotoPath { get; set; }
    [Column("device_id")]
    public int DeviceId { get; set; }
    }
}
