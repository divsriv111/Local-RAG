using System.Security.Claims;
using Application.DTOs;
using Application.Features.ChatHistories.Commands;
using Application.Features.ChatHistories.Queries;
using Application.Features.Messages.Commands;
using Application.Features.Messages.Queries;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api")]
[Authorize]
public class ChatHistoriesController : ControllerBase
{
    private readonly IMediator _mediator;

    public ChatHistoriesController(IMediator mediator)
    {
        _mediator = mediator;
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
    /// Create new chat history for a workspace
    /// </summary>
    [HttpPost("workspaces/{workspaceId}/chats")]
    [ProducesResponseType(typeof(ChatHistoryDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ChatHistoryDto>> CreateChatHistory(Guid workspaceId)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var command = new CreateChatHistoryCommand(workspaceId, userId);
            var chatHistory = await _mediator.Send(command);
            return CreatedAtAction(
                nameof(GetMessages),
                new { chatId = chatHistory.Id },
                chatHistory);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Get all chat histories for a workspace
    /// </summary>
    [HttpGet("workspaces/{workspaceId}/chats")]
    [ProducesResponseType(typeof(IEnumerable<ChatHistoryListItemDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<ChatHistoryListItemDto>>> GetChatHistories(
        Guid workspaceId,
        [FromQuery] bool includeArchived = false)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var query = new GetChatHistoriesByWorkspaceQuery(workspaceId, userId, includeArchived);
            var chatHistories = await _mediator.Send(query);
            return Ok(chatHistories);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Get all messages for a chat with pagination
    /// </summary>
    [HttpGet("chats/{chatId}/messages")]
    [ProducesResponseType(typeof(PaginatedMessagesDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<PaginatedMessagesDto>> GetMessages(
        Guid chatId,
        [FromQuery] int pageNumber = 1,
        [FromQuery] int pageSize = 50)
    {
        try
        {
            if (pageNumber < 1) pageNumber = 1;
            if (pageSize < 1 || pageSize > 100) pageSize = 50;

            var userId = GetAuthenticatedUserId();
            var query = new GetMessagesByChatHistoryQuery(chatId, userId, pageNumber, pageSize);
            var messages = await _mediator.Send(query);
            return Ok(messages);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Add new message to a chat
    /// </summary>
    [HttpPost("chats/{chatId}/messages")]
    [ProducesResponseType(typeof(MessageDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<MessageDto>> CreateMessage(
        Guid chatId,
        [FromBody] CreateMessageDto dto)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(dto.Content))
            {
                return BadRequest(new { message = "Message content is required." });
            }

            var userId = GetAuthenticatedUserId();
            var command = new CreateMessageCommand(
                chatId,
                userId,
                dto.Content,
                dto.IsUserMessage,
                dto.References);
            var message = await _mediator.Send(command);
            return CreatedAtAction(
                nameof(GetMessages),
                new { chatId = message.ChatHistoryId },
                message);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Archive a chat history
    /// </summary>
    [HttpPut("chats/{chatId}/archive")]
    [ProducesResponseType(typeof(ChatHistoryDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ChatHistoryDto>> ArchiveChatHistory(Guid chatId)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var command = new ArchiveChatHistoryCommand(chatId, userId);
            var chatHistory = await _mediator.Send(command);
            return Ok(chatHistory);
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Delete a chat history (cascades to all messages)
    /// </summary>
    [HttpDelete("chats/{chatId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> DeleteChatHistory(Guid chatId)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var command = new DeleteChatHistoryCommand(chatId, userId);
            var result = await _mediator.Send(command);

            if (!result)
            {
                return NotFound(new { message = "Chat history not found or you don't have permission to delete it." });
            }

            return NoContent();
        }
        catch (UnauthorizedAccessException ex)
        {
            return StatusCode(StatusCodes.Status403Forbidden, new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred.",
                error = ex.Message
            });
        }
    }
}
