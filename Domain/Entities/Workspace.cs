namespace Domain.Entities;

public class Workspace
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public Guid UserId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }

    // Navigation properties
    public User User { get; set; } = null!;
    public ICollection<ChatHistory> ChatHistories { get; set; } = new List<ChatHistory>();
    public ICollection<PDFDocument> PDFDocuments { get; set; } = new List<PDFDocument>();
}
