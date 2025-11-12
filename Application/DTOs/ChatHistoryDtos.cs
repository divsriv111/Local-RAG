namespace Application.DTOs;

public record ChatHistoryDto
{
    public Guid Id { get; init; }
    public Guid WorkspaceId { get; init; }
    public string Name { get; init; } = string.Empty;
    public string FirstQuery { get; init; } = string.Empty;
    public DateTime CreatedAt { get; init; }
    public bool IsArchived { get; init; }
    public int MessageCount { get; init; }
}

public record CreateChatHistoryDto
{
    public Guid WorkspaceId { get; init; }
    public string FirstQuery { get; init; } = string.Empty;
}

public record UpdateChatHistoryDto
{
    public string? Name { get; init; }
    public bool? IsArchived { get; init; }
}

public record ChatHistoryListItemDto
{
    public Guid Id { get; init; }
    public string Name { get; init; } = string.Empty;
    public DateTime CreatedAt { get; init; }
    public bool IsArchived { get; init; }
    public int MessageCount { get; init; }
}
