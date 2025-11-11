namespace Domain.Entities;

public class ChatHistory
{
    public Guid Id { get; set; }
    public Guid WorkspaceId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string FirstQuery { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public bool IsArchived { get; set; }

    // Navigation properties
    public Workspace Workspace { get; set; } = null!;
    public ICollection<Message> Messages { get; set; } = new List<Message>();
}
