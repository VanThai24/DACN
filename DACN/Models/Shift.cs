using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

using System.ComponentModel.DataAnnotations.Schema;
namespace Models
{
    [Table("shifts")]
    public class Shift
    {
        [Key]
        public int Id { get; set; }
    [Column("employee_id")]
    public int EmployeeId { get; set; }
        public DateTime? Date { get; set; }
    [Column("start_time")]
    public TimeSpan? StartTime { get; set; }
    [Column("end_time")]
    public TimeSpan? EndTime { get; set; }
    [Column("is_overtime")]
    public bool IsOvertime { get; set; } = false;
    [Column("overtime_note")]
    [StringLength(500)]
    public string? OvertimeNote { get; set; }
    }
}
