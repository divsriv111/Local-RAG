namespace Application.DTOs;

public record LlmQueryRequestDto
{
    public string Query { get; init; } = string.Empty;
    public Guid[] SelectedPdfIds { get; init; } = Array.Empty<Guid>();
    public Guid WorkspaceId { get; init; }
    public Guid ChatHistoryId { get; init; }
    public string LlmModel { get; init; } = string.Empty;
}

public record LlmQueryResponseDto
{
    public string Answer { get; init; } = string.Empty;
    public SourceReference[] References { get; init; } = Array.Empty<SourceReference>();
    public ProcessingMetadata Metadata { get; init; } = new();
}

public record SourceReference
{
    public string PdfName { get; init; } = string.Empty;
    public int PageNumber { get; init; }
    public Guid PdfId { get; init; }
}

public record ProcessingMetadata
{
    public string ModelUsed { get; init; } = string.Empty;
    public DateTime Timestamp { get; init; }
    public int TokenCount { get; init; }
    public double ProcessingTimeMs { get; init; }
}

// DTOs for communication with Python service
public record PythonLlmRequest
{
    public string Query { get; init; } = string.Empty;
    public string WorkspaceId { get; init; } = string.Empty;
    public string[] PdfIds { get; init; } = Array.Empty<string>();
    public string ChatHistoryId { get; init; } = string.Empty;
    public string ModelName { get; init; } = string.Empty;
    public List<ChatMessage> ChatHistory { get; init; } = new();
}

public record ChatMessage
{
    public string Role { get; init; } = string.Empty; // "user" or "assistant"
    public string Content { get; init; } = string.Empty;
}

// DTOs for streaming responses from Python service
public record StreamChunk
{
    public string Type { get; init; } = string.Empty; // "token", "source", "done", "error"
    public string? Content { get; init; }
    public string? Pdf { get; init; }
    public int? Page { get; init; }
    public string? Answer { get; init; }
    public List<PythonSourceReference>? References { get; init; }
    public string? Message { get; init; }
}

public record PythonSourceReference
{
    public string Pdf { get; init; } = string.Empty;
    public int Page { get; init; }
}
