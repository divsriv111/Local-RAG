namespace Application.DTOs;

public record PDFDocumentDto
{
    public Guid Id { get; init; }
    public Guid WorkspaceId { get; init; }
    public string FileName { get; init; } = string.Empty;
    public string FilePath { get; init; } = string.Empty;
    public long FileSize { get; init; }
    public DateTime UploadedAt { get; init; }
    public bool IsSelected { get; init; }
}

public record UploadPDFDto
{
    public Guid WorkspaceId { get; init; }
    public string FileName { get; init; } = string.Empty;
    public string FilePath { get; init; } = string.Empty;
    public long FileSize { get; init; }
}
