# Structured Logging Configuration Guide

## Overview

This document describes the structured logging implementation in the RAG Chatbot API using Serilog and Elasticsearch.

## Features Implemented

### 1. Logging Infrastructure

- **Serilog** as the logging framework
- **Elasticsearch** as the log aggregation backend
- **Console** output for local development
- **File sink** for Elasticsearch failure backup

### 2. Log Enrichment

All logs are automatically enriched with:

- **Machine Name**: Identifies which server generated the log
- **Thread ID**: Useful for debugging multi-threaded operations
- **Environment Name**: Development, Staging, Production
- **Application Name**: "RAG-Chatbot-API"
- **Timestamp**: UTC timestamp for all log entries

### 3. Correlation ID Tracking

- Automatically generates a unique `Guid` for each request
- Included in response headers as `X-Correlation-ID`
- Propagates through the entire request pipeline
- Can be passed to external services (Python LLM service) for distributed tracing

### 4. Request Logging

All HTTP requests are logged with:

- HTTP Method (GET, POST, PUT, DELETE, etc.)
- Request Path
- Status Code
- Elapsed Time (in milliseconds)
- Request Host and Scheme
- Remote IP Address
- User Agent
- Correlation ID

### 5. Custom Application Events

The `IApplicationLoggingService` provides structured logging for:

#### Authentication Events

- `LogAuthenticationAttempt(username, success, errorMessage)`
- `LogUserRegistration(username, email, success, errorMessage)`

#### Workspace Operations

- `LogWorkspaceCreated(workspaceId, workspaceName, userId)`
- `LogWorkspaceUpdated(workspaceId, oldName, newName, userId)`
- `LogWorkspaceDeleted(workspaceId, workspaceName, userId)`

#### PDF Upload Events

- `LogPdfUploadStarted(workspaceId, fileName, fileSize, userId)`
- `LogPdfUploadCompleted(pdfId, workspaceId, fileName, fileSize, duration, success, errorMessage)`

#### LLM Query Events

- `LogLlmQueryStarted(chatHistoryId, model, queryLength, workspaceId, selectedPdfIds)`
- `LogLlmQueryCompleted(chatHistoryId, model, queryLength, responseLength, responseTime, success, errorMessage)`

#### Chat History Events

- `LogChatHistoryCreated(chatHistoryId, workspaceId, chatName, userId)`
- `LogChatHistoryDeleted(chatHistoryId, chatName, workspaceId, userId)`
- `LogChatHistoryArchived(chatHistoryId, chatName, isArchived, userId)`

#### Exception Logging

- `LogException(exception, context, additionalData)`
  - Captures exception type, message, and stack trace
  - Supports additional contextual data

## Configuration

### appsettings.json

```json
{
  "Elasticsearch": {
    "Uri": "http://localhost:9200",
    "IndexPrefix": "rag-chatbot-logs",
    "Username": "",
    "Password": ""
  },
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.Hosting.Lifetime": "Information",
        "System": "Warning"
      }
    }
  },
  "LogRetention": {
    "RetentionDays": 30,
    "Description": "Logs older than this will be deleted from Elasticsearch"
  }
}
```

### Environment Variables (Production)

For production deployments, override settings using environment variables:

```bash
Elasticsearch__Uri=http://elasticsearch:9200
Elasticsearch__Username=your_username
Elasticsearch__Password=your_secure_password
Elasticsearch__IndexPrefix=prod-rag-chatbot-logs
```

## Elasticsearch Index Structure

### Index Naming Pattern

- Format: `{IndexPrefix}-yyyy.MM.dd`
- Example: `rag-chatbot-logs-2025.11.11`
- Daily rotation for better performance and easier retention management

### Index Settings

- **Shards**: 2
- **Replicas**: 1
- **Auto-register template**: Enabled
- **ES Version**: 7.x compatible

## Log Levels

| Level           | Usage                                                       |
| --------------- | ----------------------------------------------------------- |
| **Information** | Normal application flow (successful operations)             |
| **Warning**     | Unexpected but handled situations (authentication failures) |
| **Error**       | Errors and exceptions that need attention                   |
| **Fatal**       | Critical failures that cause application shutdown           |

## Usage Examples

### In Controllers

```csharp
public class AuthController : ControllerBase
{
    private readonly IApplicationLoggingService _loggingService;

    public AuthController(IApplicationLoggingService loggingService)
    {
        _loggingService = loggingService;
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginDto loginDto)
    {
        try
        {
            var result = await _authService.LoginAsync(loginDto);

            if (result.Success)
            {
                _loggingService.LogAuthenticationAttempt(loginDto.Username, true);
                return Ok(result);
            }
            else
            {
                _loggingService.LogAuthenticationAttempt(loginDto.Username, false, "Invalid credentials");
                return Unauthorized();
            }
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "Login endpoint", new Dictionary<string, object>
            {
                { "Username", loginDto.Username },
                { "IPAddress", HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown" }
            });
            return StatusCode(500);
        }
    }
}
```

### For PDF Uploads

```csharp
var startTime = DateTime.UtcNow;
_loggingService.LogPdfUploadStarted(workspaceId, file.FileName, file.Length, userId);

try
{
    var pdfId = await _pdfService.UploadAsync(file, workspaceId);
    var duration = DateTime.UtcNow - startTime;

    _loggingService.LogPdfUploadCompleted(
        pdfId,
        workspaceId,
        file.FileName,
        file.Length,
        duration,
        success: true
    );
}
catch (Exception ex)
{
    var duration = DateTime.UtcNow - startTime;
    _loggingService.LogPdfUploadCompleted(
        Guid.Empty,
        workspaceId,
        file.FileName,
        file.Length,
        duration,
        success: false,
        errorMessage: ex.Message
    );
    throw;
}
```

### For LLM Queries

```csharp
var startTime = DateTime.UtcNow;
_loggingService.LogLlmQueryStarted(
    chatHistoryId,
    model,
    query.Length,
    workspaceId,
    selectedPdfIds
);

try
{
    var response = await _llmService.QueryAsync(query, model, selectedPdfIds);
    var responseTime = DateTime.UtcNow - startTime;

    _loggingService.LogLlmQueryCompleted(
        chatHistoryId,
        model,
        query.Length,
        response.Length,
        responseTime,
        success: true
    );
}
catch (Exception ex)
{
    var responseTime = DateTime.UtcNow - startTime;
    _loggingService.LogLlmQueryCompleted(
        chatHistoryId,
        model,
        query.Length,
        0,
        responseTime,
        success: false,
        errorMessage: ex.Message
    );
    throw;
}
```

## Viewing Logs

### Kibana Setup

1. **Access Kibana**: http://localhost:5601 (or your production URL)

2. **Create Index Pattern**:

   - Go to Management → Stack Management → Index Patterns
   - Click "Create index pattern"
   - Index pattern name: `rag-chatbot-logs-*`
   - Time field: `@timestamp`
   - Click "Create index pattern"

3. **Useful Queries**:

   ```
   # All authentication failures
   MessageTemplate: "Authentication failed*"

   # All errors in the last hour
   Level: "Error" AND @timestamp > now-1h

   # Specific correlation ID
   CorrelationId: "YOUR-CORRELATION-ID-HERE"

   # PDF uploads over 10MB
   FileSize > 10485760

   # LLM queries taking over 5 seconds
   ResponseTime > 5000

   # All requests from a specific user
   UserId: "USER-GUID-HERE"
   ```

4. **Create Visualizations**:
   - **Line Chart**: Authentication attempts over time
   - **Pie Chart**: Error distribution by type
   - **Metric**: Average LLM response time
   - **Data Table**: Recent PDF uploads with size and duration

### Log Retention

**Default Retention**: 30 days (configured in `appsettings.json`)

#### Manual Cleanup

```bash
# Delete indices older than 30 days
curl -X DELETE "localhost:9200/rag-chatbot-logs-*" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"range": {"@timestamp": {"lt": "now-30d"}}}}'
```

#### Automatic Cleanup (Elasticsearch ILM)

Set up Index Lifecycle Management in Elasticsearch:

1. Create ILM policy:

```json
PUT _ilm/policy/rag-chatbot-logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {}
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

2. Apply to index template (auto-registered by Serilog)

## Monitoring & Alerts

### Recommended Alerts

1. **High Error Rate**: More than 10 errors per minute
2. **Authentication Failures**: More than 5 failed attempts for the same user within 5 minutes
3. **Slow LLM Queries**: Queries taking longer than 30 seconds
4. **Large PDF Uploads**: Files larger than 40MB
5. **Elasticsearch Connection Issues**: Check `elasticsearch-failures-*.txt` logs

### Health Check Endpoint

Add to your API:

```csharp
app.MapGet("/health/logs", () =>
{
    // Check if Elasticsearch is reachable
    // Return health status
});
```

## Distributed Tracing

### Passing Correlation ID to Python Service

In `LlmService.cs`:

```csharp
var correlationId = _httpContextAccessor.HttpContext?.Items["X-Correlation-ID"]?.ToString();

var request = new HttpRequestMessage(HttpMethod.Post, "/api/llm/query");
request.Headers.Add("X-Correlation-ID", correlationId);
```

In Python service, add the same header to logs:

```python
correlation_id = request.headers.get("X-Correlation-ID")
logger.info("Processing query", extra={"correlation_id": correlation_id})
```

## Troubleshooting

### Logs Not Appearing in Elasticsearch

1. Check Elasticsearch is running:

   ```bash
   curl http://localhost:9200/_cluster/health
   ```

2. Check `./logs/elasticsearch-failures-*.txt` for errors

3. Verify Elasticsearch URI in `appsettings.json`

4. Check authentication credentials if using secured Elasticsearch

### Performance Issues

1. **Reduce log volume**: Increase `MinimumLevel` to `Warning`
2. **Optimize Elasticsearch**: Increase heap size, add more nodes
3. **Use async logging**: Serilog uses batching by default
4. **Rotate indices**: Daily rotation is optimal for most cases

### Missing Correlation IDs

Ensure `CorrelationIdMiddleware` is registered **before** other middleware:

```csharp
app.UseCorrelationId(); // Must be early in pipeline
app.UseSerilogRequestLogging();
```

## Security Considerations

1. **Sensitive Data**: Never log passwords, tokens, or API keys
2. **PII Protection**: Mask or hash personal information in logs
3. **Elasticsearch Security**: Enable authentication and TLS in production
4. **Log Retention**: Comply with data retention policies (GDPR, etc.)
5. **Access Control**: Restrict Kibana access to authorized users only

## Performance Impact

- **Console Logging**: Minimal (< 1ms per log)
- **Elasticsearch Logging**: Batched, minimal impact (< 5ms per batch)
- **Enrichers**: Negligible (< 0.1ms)
- **Request Logging**: < 1ms per request

**Total overhead**: Less than 2% in most scenarios

## Best Practices

1. **Use structured logging**: Always use Serilog's structured syntax

   ```csharp
   // Good
   _logger.LogInformation("User {UserId} uploaded {FileName}", userId, fileName);

   // Bad
   _logger.LogInformation($"User {userId} uploaded {fileName}");
   ```

2. **Log at appropriate levels**: Don't use `Information` for debugging

3. **Include context**: Add relevant data (IDs, names, sizes) to logs

4. **Use correlation IDs**: Essential for debugging distributed systems

5. **Monitor log volume**: High volume can impact performance and costs

6. **Test logging**: Verify logs appear correctly in Elasticsearch

7. **Document log events**: Keep this guide updated with new log types

---

## Maintenance

- **Review retention policy**: Quarterly
- **Update Elasticsearch**: Keep current with security patches
- **Optimize indices**: Reindex if performance degrades
- **Backup important logs**: Export critical events to long-term storage
- **Train team**: Ensure developers understand logging best practices

For questions or issues, contact the DevOps team.
