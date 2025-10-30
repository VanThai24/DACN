using System;
using System.ComponentModel.DataAnnotations;

namespace Models
{
    public class Attendance
    {
        [Key]
        public int Id { get; set; }
        public int EmployeeId { get; set; }
        public DateTime Date { get; set; }
        public bool IsPresent { get; set; }
        // Thêm các trường khác nếu cần
    }
}
