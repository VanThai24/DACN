using System.ComponentModel.DataAnnotations;

using System.ComponentModel.DataAnnotations.Schema;
namespace Models
{
    [Table("employees")]
    public class Employee
    {
        [Key]
        public int Id { get; set; }
        public string? Name { get; set; }
        public string? Department { get; set; }
        [Column("role")]
        public string Role { get; set; } = "employee";
    [Column("phone")]
    public string? Phone { get; set; }

    [Column("email")]
    public string? Email { get; set; }
        [Column("face_embedding")]
        public byte[]? FaceEmbedding { get; set; }

        [Column("photo_path")]
        public string? PhotoPath { get; set; }

        [Column("is_locked")]
        public bool IsLocked { get; set; }
    }
}
