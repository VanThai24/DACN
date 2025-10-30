using System;
using System.ComponentModel.DataAnnotations;

using System.ComponentModel.DataAnnotations.Schema;
namespace Models
{
    public class Report
    {
        [Key]
        public int Id { get; set; }
    [Column("created_at")]
    public DateTime? CreatedAt { get; set; }
    public string? Type { get; set; }
    [Column("file_path")]
    public string? FilePath { get; set; }
    [Column("created_by")]
    public int CreatedBy { get; set; }
    }
}
