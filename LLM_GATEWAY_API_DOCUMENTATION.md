# LLM Gateway API Implementation

## Overview

This implementation provides an ASP.NET Core 9 API controller that acts as a gateway to the Python LLM (Large Language Model) service. It supports both standard HTTP responses and Server-Sent Events (SSE) for real-time streaming of LLM responses.

## Components

### 1. DTOs (Data Transfer Objects)

**Location:** `Application/DTOs/LlmDtos.cs`

#### Request DTO

```csharp
public record LlmQueryRequestDto
{
    public string Query { get; init; }
    public Guid[] SelectedPdfIds { get; init; }
    public Guid WorkspaceId { get; init; }
    public Guid ChatHistoryId { get; init; }
    public string LlmModel { get; init; }
}
```

#### Response DTO

```csharp
public record LlmQueryResponseDto
{
    public string Answer { get; init; }
    public SourceReference[] References { get; init; }
    public ProcessingMetadata Metadata { get; init; }
}
```

### 2. Service Interface & Implementation

**Interface:** `Application/Interfaces/ILlmService.cs`

Key methods:

- `QueryAsync()` - Standard HTTP request/response
- `QueryStreamAsync()` - Server-Sent Events (SSE) streaming
- `IsServiceAvailableAsync()` - Health check

**Implementation:** `Infrastructure/Services/LlmService.cs`

Features:

- HttpClient configuration with 5-minute timeout
- Retry policies using Polly (3 retries with exponential backoff)
- Streaming response support
- Error handling and logging

### 3. Controller

**Location:** `API/Controllers/LlmController.cs`

#### Endpoints

##### POST /api/llm/query

Sends a query to the Python LLM service with optional streaming support.

**Request Headers:**

- `Authorization: Bearer {token}` (required)
- `Accept: text/event-stream` (optional, for streaming)

**Request Body:**

```json
{
  "query": "What is this document about?",
  "selectedPdfIds": ["guid1", "guid2"],
  "workspaceId": "workspace-guid",
  "chatHistoryId": "chat-guid",
  "llmModel": "gpt-4-turbo"
}
```

**Response (Non-streaming):**

```json
{
  "answer": "The document discusses...",
  "references": [
    {
      "pdfName": "document.pdf",
      "pageNumber": 5,
      "pdfId": "guid"
    }
  ],
  "metadata": {
    "modelUsed": "gpt-4-turbo",
    "timestamp": "2025-11-11T10:00:00Z",
    "tokenCount": 150,
    "processingTimeMs": 2500
  }
}
```

**Streaming Response (SSE):**

```
data: {"type":"token","content":"The"}

data: {"type":"token","content":" document"}

data: {"type":"source","pdf":"document.pdf","page":5}

data: {"type":"done","answer":"The document...","references":[...]}
```

##### GET /api/llm/health

Checks if the Python LLM service is available.

**Response:**

```json
{
  "status": "available",
  "timestamp": "2025-11-11T10:00:00Z"
}
```

## Configuration

### appsettings.json

```json
{
  "PythonService": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

### Dependency Injection

**Infrastructure/DependencyInjection.cs:**

```csharp
services.AddHttpClient<ILlmService, LlmService>()
    .SetHandlerLifetime(TimeSpan.FromMinutes(10))
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetTimeoutPolicy());
```

**Retry Policy:**

- 3 retries
- Exponential backoff: 2^retryCount seconds
- Handles transient HTTP errors and 503 Service Unavailable

**Timeout Policy:**

- 5 minutes (300 seconds)

## Features

### 1. Authentication & Authorization

- JWT Bearer token authentication required
- User ownership validation for workspaces
- Workspace and chat history validation

### 2. Request Validation

- Query cannot be empty
- At least one PDF must be selected
- LLM model must be specified
- Workspace must exist and belong to user
- Chat history must exist and belong to workspace

### 3. Message Storage

- User query saved to database before processing
- Assistant response saved after completion
- References stored as JSON

### 4. Streaming Support

- Automatic detection via `Accept: text/event-stream` header
- Real-time token-by-token streaming
- Accumulates full response for database storage
- Graceful error handling in streams

### 5. Error Handling

- HTTP 400: Bad request (validation errors)
- HTTP 401: Unauthorized
- HTTP 403: Forbidden (workspace ownership)
- HTTP 404: Not found (workspace/chat history)
- HTTP 408: Request timeout
- HTTP 503: Service unavailable
- HTTP 500: Internal server error

### 6. Logging

- Request/response logging
- Performance metrics
- Error logging with stack traces
- Correlation IDs for distributed tracing

## Supported LLM Models

- `gpt-4-turbo` - OpenAI GPT-4 Turbo
- `gpt-4o-mini` - OpenAI GPT-4.1 Mini
- `gpt-4.1-mini` - Alternative name for GPT-4.1 Mini
- `local-llama-3` - Local LLaMA 3 model
- `local-mistral` - Local Mistral model

## Testing

### Using the HTTP file

See `API/LlmQuery.http` for example requests.

### Manual Testing

```bash
# Health check
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/llm/health

# Standard query
curl -X POST http://localhost:5000/api/llm/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this about?",
    "selectedPdfIds": ["guid1"],
    "workspaceId": "workspace-guid",
    "chatHistoryId": "chat-guid",
    "llmModel": "gpt-4o-mini"
  }'

# Streaming query
curl -X POST http://localhost:5000/api/llm/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "query": "Summarize this document",
    "selectedPdfIds": ["guid1"],
    "workspaceId": "workspace-guid",
    "chatHistoryId": "chat-guid",
    "llmModel": "gpt-4-turbo"
  }'
```

## Python Service Integration

The API expects the Python service to implement the following:

### Endpoint: POST /api/llm/query

**Request:**

```json
{
  "query": "string",
  "workspace_id": "string",
  "pdf_ids": ["string"],
  "chat_history_id": "string",
  "model_name": "string",
  "chat_history": []
}
```

**Response (Non-streaming):**

```json
{
  "answer": "string",
  "references": [{ "pdf": "string", "page": 0 }]
}
```

**Streaming Response (SSE):**

```
data: {"type":"token","content":"word"}
data: {"type":"source","pdf":"file.pdf","page":5}
data: {"type":"done","answer":"...","references":[...]}
data: {"type":"error","message":"error text"}
```

### Endpoint: GET /health

**Response:**

```json
{
  "status": "healthy"
}
```

## Performance Considerations

1. **Timeouts:**

   - HttpClient: 5 minutes
   - Handler lifetime: 10 minutes

2. **Retry Policy:**

   - Max 3 retries
   - Exponential backoff prevents overwhelming the service

3. **Streaming:**

   - Lower memory usage for large responses
   - Better user experience with real-time feedback
   - Connection kept alive during processing

4. **Database:**
   - Messages saved after LLM response
   - References stored as JSON for flexibility
   - Timestamps in UTC for consistency

## Security Considerations

1. **Authentication:** JWT token required for all endpoints
2. **Authorization:** User ownership verified for workspaces
3. **Validation:** All inputs validated before processing
4. **Error Messages:** Generic error messages to prevent information leakage
5. **Logging:** Sensitive data excluded from logs

## Future Enhancements

1. Rate limiting per user/workspace
2. Query cost tracking (token usage)
3. Cache frequently asked questions
4. Support for conversation history in requests
5. Webhook support for long-running queries
6. Multi-language support for queries
7. Advanced filtering and ranking of PDF chunks
8. Custom prompt templates per workspace
9. Fine-tuned model support
10. Analytics and usage dashboards

## Dependencies

### NuGet Packages

**Application Layer:**

- Microsoft.Extensions.Http (9.0.0)
- Microsoft.Extensions.Http.Polly (9.0.0)
- Polly (8.5.0)
- Polly.Extensions.Http (3.0.0)

**Infrastructure Layer:**

- Microsoft.Extensions.Http (9.0.0)
- Microsoft.Extensions.Http.Polly (9.0.0)
- Polly (8.5.0)
- Polly.Extensions.Http (3.0.0)

## Troubleshooting

### Service Unavailable (503)

- Check Python service is running: `curl http://localhost:8000/health`
- Verify `PythonService:BaseUrl` in appsettings.json
- Check network connectivity

### Timeout (408)

- Increase timeout in `GetTimeoutPolicy()` if needed
- Check Python service performance
- Reduce number of PDFs selected

### Streaming Not Working

- Ensure `Accept: text/event-stream` header is set
- Check client supports SSE (EventSource API)
- Verify firewall/proxy allows streaming

### No References in Response

- Verify Python service includes references in response
- Check PDF processing in vector database
- Validate PDF IDs are correct

## Contact & Support

For issues or questions:

- Check logs in Elasticsearch/Kibana
- Review API documentation at `/swagger`
- Contact development team
