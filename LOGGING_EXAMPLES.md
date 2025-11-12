# Logging Implementation Examples

## How to Use IApplicationLoggingService in Controllers

Below are practical examples showing how to integrate structured logging into your controllers.

---

## Example 1: Authentication Controller

```csharp
using Application.DTOs;
using Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IAuthenticationService _authService;
    private readonly IApplicationLoggingService _loggingService;

    public AuthController(
        IAuthenticationService authService,
        IApplicationLoggingService loggingService)
    {
        _authService = authService;
        _loggingService = loggingService;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterDto dto)
    {
        try
        {
            var result = await _authService.RegisterAsync(dto);
            
            _loggingService.LogUserRegistration(
                dto.Username,
                dto.Email,
                success: true
            );
            
            return CreatedAtAction(nameof(Register), new { id = result.UserId }, result);
        }
        catch (Exception ex)
        {
            _loggingService.LogUserRegistration(
                dto.Username,
                dto.Email,
                success: false,
                errorMessage: ex.Message
            );
            
            return BadRequest(new { error = ex.Message });
        }
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginDto dto)
    {
        try
        {
            var result = await _authService.LoginAsync(dto);
            
            if (result.Success)
            {
                _loggingService.LogAuthenticationAttempt(dto.Username, success: true);
                return Ok(new { token = result.Token, refreshToken = result.RefreshToken });
            }
            else
            {
                _loggingService.LogAuthenticationAttempt(
                    dto.Username,
                    success: false,
                    errorMessage: "Invalid username or password"
                );
                return Unauthorized(new { error = "Invalid credentials" });
            }
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "Login endpoint", new Dictionary<string, object>
            {
                { "Username", dto.Username },
                { "IPAddress", HttpContext.Connection.RemoteIpAddress?.ToString() ?? "unknown" }
            });
            
            return StatusCode(500, new { error = "An error occurred during login" });
        }
    }
}
```

---

## Example 2: Workspaces Controller

```csharp
using Application.DTOs;
using Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class WorkspacesController : ControllerBase
{
    private readonly IWorkspaceService _workspaceService;
    private readonly IApplicationLoggingService _loggingService;

    public WorkspacesController(
        IWorkspaceService workspaceService,
        IApplicationLoggingService loggingService)
    {
        _workspaceService = workspaceService;
        _loggingService = loggingService;
    }

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        return Guid.Parse(userIdClaim!);
    }

    [HttpPost]
    public async Task<IActionResult> CreateWorkspace([FromBody] CreateWorkspaceDto dto)
    {
        try
        {
            var userId = GetCurrentUserId();
            var workspace = await _workspaceService.CreateAsync(dto, userId);
            
            _loggingService.LogWorkspaceCreated(
                workspace.Id,
                workspace.Name,
                userId
            );
            
            return CreatedAtAction(nameof(GetWorkspace), new { id = workspace.Id }, workspace);
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "CreateWorkspace endpoint", new Dictionary<string, object>
            {
                { "WorkspaceName", dto.Name },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to create workspace" });
        }
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetWorkspace(Guid id)
    {
        var workspace = await _workspaceService.GetByIdAsync(id);
        
        if (workspace == null)
        {
            return NotFound();
        }
        
        return Ok(workspace);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateWorkspace(Guid id, [FromBody] UpdateWorkspaceDto dto)
    {
        try
        {
            var userId = GetCurrentUserId();
            var oldWorkspace = await _workspaceService.GetByIdAsync(id);
            
            if (oldWorkspace == null)
            {
                return NotFound();
            }
            
            var updatedWorkspace = await _workspaceService.UpdateAsync(id, dto, userId);
            
            _loggingService.LogWorkspaceUpdated(
                id,
                oldWorkspace.Name,
                dto.Name,
                userId
            );
            
            return Ok(updatedWorkspace);
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "UpdateWorkspace endpoint", new Dictionary<string, object>
            {
                { "WorkspaceId", id },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to update workspace" });
        }
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteWorkspace(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var workspace = await _workspaceService.GetByIdAsync(id);
            
            if (workspace == null)
            {
                return NotFound();
            }
            
            await _workspaceService.DeleteAsync(id, userId);
            
            _loggingService.LogWorkspaceDeleted(
                id,
                workspace.Name,
                userId
            );
            
            return NoContent();
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "DeleteWorkspace endpoint", new Dictionary<string, object>
            {
                { "WorkspaceId", id },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to delete workspace" });
        }
    }
}
```

---

## Example 3: PDF Upload Controller

```csharp
using Application.DTOs;
using Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Security.Claims;

namespace API.Controllers;

[ApiController]
[Route("api/workspaces/{workspaceId}/pdfs")]
[Authorize]
public class PDFsController : ControllerBase
{
    private readonly IPdfService _pdfService;
    private readonly IApplicationLoggingService _loggingService;

    public PDFsController(
        IPdfService pdfService,
        IApplicationLoggingService loggingService)
    {
        _pdfService = pdfService;
        _loggingService = loggingService;
    }

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        return Guid.Parse(userIdClaim!);
    }

    [HttpPost("upload")]
    [RequestSizeLimit(52428800)] // 50MB
    public async Task<IActionResult> UploadPdf(Guid workspaceId, [FromForm] IFormFile file)
    {
        var stopwatch = Stopwatch.StartNew();
        var userId = GetCurrentUserId();
        
        try
        {
            if (file == null || file.Length == 0)
            {
                return BadRequest(new { error = "No file provided" });
            }

            _loggingService.LogPdfUploadStarted(
                workspaceId,
                file.FileName,
                file.Length,
                userId
            );

            var pdfId = await _pdfService.UploadAsync(file, workspaceId, userId);
            stopwatch.Stop();
            
            _loggingService.LogPdfUploadCompleted(
                pdfId,
                workspaceId,
                file.FileName,
                file.Length,
                stopwatch.Elapsed,
                success: true
            );

            return Ok(new 
            { 
                id = pdfId, 
                fileName = file.FileName,
                size = file.Length,
                uploadDuration = stopwatch.ElapsedMilliseconds
            });
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            
            _loggingService.LogPdfUploadCompleted(
                Guid.Empty,
                workspaceId,
                file?.FileName ?? "unknown",
                file?.Length ?? 0,
                stopwatch.Elapsed,
                success: false,
                errorMessage: ex.Message
            );
            
            _loggingService.LogException(ex, "PDF Upload", new Dictionary<string, object>
            {
                { "WorkspaceId", workspaceId },
                { "FileName", file?.FileName ?? "unknown" },
                { "FileSize", file?.Length ?? 0 },
                { "UserId", userId }
            });

            return StatusCode(500, new { error = "Failed to upload PDF" });
        }
    }
}
```

---

## Example 4: LLM Query Controller

```csharp
using Application.DTOs;
using Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Security.Claims;

namespace API.Controllers;

[ApiController]
[Route("api/llm")]
[Authorize]
public class LlmController : ControllerBase
{
    private readonly ILlmService _llmService;
    private readonly IApplicationLoggingService _loggingService;

    public LlmController(
        ILlmService llmService,
        IApplicationLoggingService loggingService)
    {
        _llmService = llmService;
        _loggingService = loggingService;
    }

    [HttpPost("query")]
    public async Task<IActionResult> Query([FromBody] LlmQueryDto dto)
    {
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            _loggingService.LogLlmQueryStarted(
                dto.ChatHistoryId,
                dto.Model,
                dto.Query.Length,
                dto.WorkspaceId,
                dto.SelectedPdfIds
            );

            var response = await _llmService.QueryAsync(dto);
            stopwatch.Stop();
            
            _loggingService.LogLlmQueryCompleted(
                dto.ChatHistoryId,
                dto.Model,
                dto.Query.Length,
                response.Answer.Length,
                stopwatch.Elapsed,
                success: true
            );

            return Ok(response);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            
            _loggingService.LogLlmQueryCompleted(
                dto.ChatHistoryId,
                dto.Model,
                dto.Query.Length,
                0,
                stopwatch.Elapsed,
                success: false,
                errorMessage: ex.Message
            );
            
            _loggingService.LogException(ex, "LLM Query", new Dictionary<string, object>
            {
                { "ChatHistoryId", dto.ChatHistoryId },
                { "Model", dto.Model },
                { "QueryLength", dto.Query.Length },
                { "WorkspaceId", dto.WorkspaceId },
                { "SelectedPdfCount", dto.SelectedPdfIds.Count }
            });

            return StatusCode(500, new { error = "Failed to process LLM query" });
        }
    }
}
```

---

## Example 5: Chat History Controller

```csharp
using Application.DTOs;
using Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace API.Controllers;

[ApiController]
[Route("api/chats")]
[Authorize]
public class ChatHistoriesController : ControllerBase
{
    private readonly IChatHistoryService _chatService;
    private readonly IApplicationLoggingService _loggingService;

    public ChatHistoriesController(
        IChatHistoryService chatService,
        IApplicationLoggingService loggingService)
    {
        _chatService = chatService;
        _loggingService = loggingService;
    }

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        return Guid.Parse(userIdClaim!);
    }

    [HttpPost]
    public async Task<IActionResult> CreateChat([FromBody] CreateChatDto dto)
    {
        try
        {
            var userId = GetCurrentUserId();
            var chat = await _chatService.CreateAsync(dto, userId);
            
            _loggingService.LogChatHistoryCreated(
                chat.Id,
                dto.WorkspaceId,
                chat.Name,
                userId
            );
            
            return CreatedAtAction(nameof(GetChat), new { id = chat.Id }, chat);
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "CreateChat endpoint", new Dictionary<string, object>
            {
                { "WorkspaceId", dto.WorkspaceId },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to create chat" });
        }
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetChat(Guid id)
    {
        var chat = await _chatService.GetByIdAsync(id);
        
        if (chat == null)
        {
            return NotFound();
        }
        
        return Ok(chat);
    }

    [HttpPut("{id}/archive")]
    public async Task<IActionResult> ArchiveChat(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var chat = await _chatService.GetByIdAsync(id);
            
            if (chat == null)
            {
                return NotFound();
            }
            
            await _chatService.ArchiveAsync(id);
            
            _loggingService.LogChatHistoryArchived(
                id,
                chat.Name,
                isArchived: true,
                userId
            );
            
            return Ok();
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "ArchiveChat endpoint", new Dictionary<string, object>
            {
                { "ChatId", id },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to archive chat" });
        }
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteChat(Guid id)
    {
        try
        {
            var userId = GetCurrentUserId();
            var chat = await _chatService.GetByIdAsync(id);
            
            if (chat == null)
            {
                return NotFound();
            }
            
            await _chatService.DeleteAsync(id);
            
            _loggingService.LogChatHistoryDeleted(
                id,
                chat.Name,
                chat.WorkspaceId,
                userId
            );
            
            return NoContent();
        }
        catch (Exception ex)
        {
            _loggingService.LogException(ex, "DeleteChat endpoint", new Dictionary<string, object>
            {
                { "ChatId", id },
                { "UserId", GetCurrentUserId() }
            });
            
            return StatusCode(500, new { error = "Failed to delete chat" });
        }
    }
}
```

---

## Key Patterns

### 1. Always Log Success and Failure
```csharp
if (success)
{
    _loggingService.LogOperationSuccess(...);
}
else
{
    _loggingService.LogOperationFailure(..., errorMessage);
}
```

### 2. Use Stopwatch for Duration Tracking
```csharp
var stopwatch = Stopwatch.StartNew();
// ... perform operation
stopwatch.Stop();
_loggingService.LogOperationCompleted(..., stopwatch.Elapsed);
```

### 3. Include Context in Exception Logs
```csharp
_loggingService.LogException(ex, "Operation name", new Dictionary<string, object>
{
    { "Key1", value1 },
    { "Key2", value2 }
});
```

### 4. Log at the Controller Level
- Controllers are the entry points
- Easy to add correlation IDs and user context
- Centralized error handling

---

## Testing Your Logs

### 1. Check Console Output
Run your API and perform operations. You should see structured logs in the console.

### 2. Query Elasticsearch
```bash
# Get recent logs
curl "http://localhost:9200/rag-chatbot-logs-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"size": 10, "sort": [{"@timestamp": "desc"}]}'
```

### 3. View in Kibana
- Navigate to Discover
- Select `rag-chatbot-logs-*` index
- Filter by log level, operation type, user, etc.

---

## Next Steps

1. Add these logging calls to your existing controllers
2. Test each endpoint to verify logs are being generated
3. Create Kibana dashboards for monitoring
4. Set up alerts for errors and anomalies
