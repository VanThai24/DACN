using System;
namespace Models
{
    public class ShiftViewModel
    {
        public int Id { get; set; }
        public string? EmployeeName { get; set; }
        public DateTime? Date { get; set; }
        public TimeSpan? StartTime { get; set; }
        public TimeSpan? EndTime { get; set; }
        public bool IsOvertime { get; set; }
        public string? OvertimeNote { get; set; }
    }
}