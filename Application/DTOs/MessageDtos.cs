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
    public string Content { get; init; } = string.Empty;
    public bool IsUserMessage { get; init; }
    public string? References { get; init; }
}

public record PaginatedMessagesDto
{
    public IEnumerable<MessageDto> Messages { get; init; } = new List<MessageDto>();
    public int TotalCount { get; init; }
    public int PageNumber { get; init; }
    public int PageSize { get; init; }
    public int TotalPages { get; init; }
}
