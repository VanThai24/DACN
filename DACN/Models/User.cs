using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Models
{
    [Table("users")]
    public class User
    {
        [Key]
        public int Id { get; set; }
        public string? Username { get; set; }
        [Column("password_hash")]
        public string? PasswordHash { get; set; }
        [Column("role")]
        public string Role { get; set; } = "employee";
        [Column("employee_id")]
        public int? EmployeeId { get; set; }
    }
}
