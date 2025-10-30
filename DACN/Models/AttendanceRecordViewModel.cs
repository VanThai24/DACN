using System;
namespace Models
{
    public class AttendanceRecordViewModel
    {
        public int Id { get; set; }
        public string? EmployeeName { get; set; }
        public DateTime? TimestampIn { get; set; }
        public DateTime? TimestampOut { get; set; }
        public string? Status { get; set; }
        public string? PhotoPath { get; set; }
        public int DeviceId { get; set; }
    }
}