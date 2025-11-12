using System.Security.Claims;
using System.Text;
using System.Text.Json;
using Application.DTOs;
using Application.Interfaces;
using Domain.Common;
using Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class LlmController : ControllerBase
{
    private readonly ILlmService _llmService;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Message> _messageRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<LlmController> _logger;

    public LlmController(
        ILlmService llmService,
        IRepository<Workspace> workspaceRepository,
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Message> messageRepository,
        IUnitOfWork unitOfWork,
        ILogger<LlmController> logger)
    {
        _llmService = llmService;
        _workspaceRepository = workspaceRepository;
        _chatHistoryRepository = chatHistoryRepository;
        _messageRepository = messageRepository;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }

    private Guid GetAuthenticatedUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid user token.");
        }
        return userId;
    }

    /// <summary>
    /// Query the LLM with streaming response support
    /// </summary>
    [HttpPost("query")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status503ServiceUnavailable)]
    public async Task<IActionResult> Query(
        [FromBody] LlmQueryRequestDto request,
        CancellationToken cancellationToken)
    {
        try
        {
            var userId = GetAuthenticatedUserId();

            // Validate request
            if (string.IsNullOrWhiteSpace(request.Query))
            {
                return BadRequest(new { error = "Query cannot be empty." });
            }

            if (request.SelectedPdfIds.Length == 0)
            {
                return BadRequest(new { error = "At least one PDF must be selected." });
            }

            if (string.IsNullOrWhiteSpace(request.LlmModel))
            {
                return BadRequest(new { error = "LLM model must be specified." });
            }

            // Verify workspace exists and belongs to user
            var workspace = await _workspaceRepository.GetByIdAsync(request.WorkspaceId, cancellationToken);

            if (workspace == null)
            {
                return NotFound(new { error = "Workspace not found." });
            }

            if (workspace.UserId != userId)
            {
                return Forbid();
            }

            // Verify chat history exists and belongs to workspace
            var chatHistory = await _chatHistoryRepository.GetByIdAsync(request.ChatHistoryId, cancellationToken);

            if (chatHistory == null)
            {
                return NotFound(new { error = "Chat history not found." });
            }

            if (chatHistory.WorkspaceId != request.WorkspaceId)
            {
                return BadRequest(new { error = "Chat history does not belong to the specified workspace." });
            }

            // Save user message to database
            var userMessage = new Message
            {
                Id = Guid.NewGuid(),
                ChatHistoryId = request.ChatHistoryId,
                Content = request.Query,
                IsUserMessage = true,
                Timestamp = DateTime.UtcNow,
                References = null
            };

            await _messageRepository.AddAsync(userMessage, cancellationToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            _logger.LogInformation(
                "User {UserId} submitted query to workspace {WorkspaceId}, chat {ChatHistoryId}",
                userId, request.WorkspaceId, request.ChatHistoryId);

            // Check if streaming is requested via Accept header
            var acceptHeader = Request.Headers["Accept"].ToString();
            if (acceptHeader.Contains("text/event-stream"))
            {
                return await StreamQueryResponse(request, cancellationToken);
            }

            // Non-streaming response
            return await ProcessQueryResponse(request, cancellationToken);
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing LLM query");
            return StatusCode(500, new { error = "An error occurred while processing your request." });
        }
    }

    private async Task<IActionResult> StreamQueryResponse(
        LlmQueryRequestDto request,
        CancellationToken cancellationToken)
    {
        Response.Headers.Append("Content-Type", "text/event-stream");
        Response.Headers.Append("Cache-Control", "no-cache");
        Response.Headers.Append("Connection", "keep-alive");

        var responseBuilder = new StringBuilder();
        var references = new List<SourceReference>();

        try
        {
            await foreach (var chunk in _llmService.QueryStreamAsync(request, cancellationToken))
            {
                // Forward the chunk to the client
                await Response.WriteAsync(chunk, cancellationToken);
                await Response.Body.FlushAsync(cancellationToken);

                // Parse chunk to accumulate data for database storage
                if (chunk.StartsWith("data: "))
                {
                    var jsonData = chunk.Substring(6).Trim();
                    try
                    {
                        var streamChunk = JsonSerializer.Deserialize<StreamChunk>(jsonData);

                        if (streamChunk != null)
                        {
                            if (streamChunk.Type == "token" && !string.IsNullOrEmpty(streamChunk.Content))
                            {
                                responseBuilder.Append(streamChunk.Content);
                            }
                            else if (streamChunk.Type == "source" && !string.IsNullOrEmpty(streamChunk.Pdf))
                            {
                                references.Add(new SourceReference
                                {
                                    PdfName = streamChunk.Pdf,
                                    PageNumber = streamChunk.Page ?? 0
                                });
                            }
                            else if (streamChunk.Type == "done")
                            {
                                // Final chunk - save assistant message to database
                                var assistantMessage = new Message
                                {
                                    Id = Guid.NewGuid(),
                                    ChatHistoryId = request.ChatHistoryId,
                                    Content = responseBuilder.ToString(),
                                    IsUserMessage = false,
                                    Timestamp = DateTime.UtcNow,
                                    References = references.Any()
                                        ? JsonSerializer.Serialize(references)
                                        : null
                                };

                                await _messageRepository.AddAsync(assistantMessage, cancellationToken);
                                await _unitOfWork.SaveChangesAsync(cancellationToken);

                                _logger.LogInformation(
                                    "Saved assistant response for chat {ChatHistoryId}, length: {Length} chars",
                                    request.ChatHistoryId, assistantMessage.Content.Length);
                            }
                        }
                    }
                    catch (JsonException ex)
                    {
                        _logger.LogWarning(ex, "Failed to parse streaming chunk for database storage");
                    }
                }
            }

            return new EmptyResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during streaming response");

            var errorChunk = new StreamChunk
            {
                Type = "error",
                Message = "An error occurred while streaming the response."
            };

            var errorData = $"data: {JsonSerializer.Serialize(errorChunk)}\n\n";
            await Response.WriteAsync(errorData, cancellationToken);
            await Response.Body.FlushAsync(cancellationToken);

            return new EmptyResult();
        }
    }

    private async Task<IActionResult> ProcessQueryResponse(
        LlmQueryRequestDto request,
        CancellationToken cancellationToken)
    {
        try
        {
            var response = await _llmService.QueryAsync(request, cancellationToken);

            // Save assistant message to database
            var assistantMessage = new Message
            {
                Id = Guid.NewGuid(),
                ChatHistoryId = request.ChatHistoryId,
                Content = response.Answer,
                IsUserMessage = false,
                Timestamp = DateTime.UtcNow,
                References = response.References.Any()
                    ? JsonSerializer.Serialize(response.References)
                    : null
            };

            await _messageRepository.AddAsync(assistantMessage, cancellationToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            _logger.LogInformation(
                "Saved assistant response for chat {ChatHistoryId}",
                request.ChatHistoryId);

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting LLM response");

            if (ex.Message.Contains("unavailable"))
            {
                return StatusCode(503, new { error = ex.Message });
            }

            if (ex.Message.Contains("timed out"))
            {
                return StatusCode(408, new { error = ex.Message });
            }

            return StatusCode(500, new { error = "An error occurred while processing your request." });
        }
    }

    /// <summary>
    /// Check if the LLM service is available
    /// </summary>
    [HttpGet("health")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status503ServiceUnavailable)]
    public async Task<IActionResult> Health(CancellationToken cancellationToken)
    {
        try
        {
            var isAvailable = await _llmService.IsServiceAvailableAsync(cancellationToken);

            if (isAvailable)
            {
                return Ok(new { status = "available", timestamp = DateTime.UtcNow });
            }

            return StatusCode(503, new { status = "unavailable", timestamp = DateTime.UtcNow });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking LLM service health");
            return StatusCode(503, new { status = "error", message = ex.Message, timestamp = DateTime.UtcNow });
        }
    }
}
