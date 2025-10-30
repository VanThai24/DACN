using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

using System.ComponentModel.DataAnnotations.Schema;
namespace Models
{
    [Table("devices")]
    public class Device
    {
        [Key]
        public int Id { get; set; }
    public string? Name { get; set; }
    public string? Location { get; set; }
    [Column("api_key")]
    public string? ApiKey { get; set; }
    [Column("last_seen")]
    public DateTime? LastSeen { get; set; }
    }
}
