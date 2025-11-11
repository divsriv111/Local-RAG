namespace Application.DTOs;

public record MessageDto
{
    public Guid Id { get; init; }
    public Guid ChatHistoryId { get; init; }
    public string Content { get; init; } = string.Empty;
    public bool IsUserMessage { get; init; }
    public DateTime Timestamp { get; init; }
    public string? References { get; init; }
}

public record CreateMessageDto
{
    public Guid ChatHistoryId { get; init; }
    public string Content { get; init; } = string.Empty;
    public bool IsUserMessage { get; init; }
    public string? References { get; init; }
}
