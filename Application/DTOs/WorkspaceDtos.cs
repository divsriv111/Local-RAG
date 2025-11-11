namespace Application.DTOs;

public record WorkspaceDto
{
    public Guid Id { get; init; }
    public string Name { get; init; } = string.Empty;
    public Guid UserId { get; init; }
    public DateTime CreatedAt { get; init; }
    public DateTime UpdatedAt { get; init; }
}

public record CreateWorkspaceDto
{
    public string Name { get; init; } = string.Empty;
}

public record UpdateWorkspaceDto
{
    public string Name { get; init; } = string.Empty;
}

public record WorkspaceDetailDto
{
    public Guid Id { get; init; }
    public string Name { get; init; } = string.Empty;
    public Guid UserId { get; init; }
    public DateTime CreatedAt { get; init; }
    public DateTime UpdatedAt { get; init; }
    public List<ChatHistoryDto> ChatHistories { get; init; } = new();
    public List<PDFDocumentDto> PDFDocuments { get; init; } = new();
}
