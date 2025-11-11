namespace Domain.Entities;

public class Message
{
    public Guid Id { get; set; }
    public Guid ChatHistoryId { get; set; }
    public string Content { get; set; } = string.Empty;
    public bool IsUserMessage { get; set; }
    public DateTime Timestamp { get; set; }
    public string? References { get; set; } // JSON stored as string

    // Navigation properties
    public ChatHistory ChatHistory { get; set; } = null!;
}
