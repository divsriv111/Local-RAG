namespace Domain.Entities;

public class PDFDocument
{
    public Guid Id { get; set; }
    public Guid WorkspaceId { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; }
    public bool IsSelected { get; set; }

    // Navigation properties
    public Workspace Workspace { get; set; } = null!;
}
