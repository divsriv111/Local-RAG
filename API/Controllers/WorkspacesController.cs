using System.Security.Claims;
using Application.DTOs;
using Application.Features.Workspaces.Commands;
using Application.Features.Workspaces.Queries;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class WorkspacesController : ControllerBase
{
    private readonly IMediator _mediator;

    public WorkspacesController(IMediator mediator)
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
    /// Get all workspaces for authenticated user
    /// </summary>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<WorkspaceDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<WorkspaceDto>>> GetAll(
        [FromQuery] string? search = null,
        [FromQuery] string sortBy = "createdAt",
        [FromQuery] string sortOrder = "desc")
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var query = new GetAllWorkspacesQuery(userId, search, sortBy, sortOrder);
            var workspaces = await _mediator.Send(query);
            return Ok(workspaces);
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
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
    /// Get workspace by ID with associated chat histories and PDFs
    /// </summary>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(WorkspaceDetailDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<WorkspaceDetailDto>> GetById(Guid id)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var query = new GetWorkspaceByIdQuery(id, userId);
            var workspace = await _mediator.Send(query);

            if (workspace == null)
                return NotFound(new { message = "Workspace not found or you don't have access to it." });

            return Ok(workspace);
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
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
    /// Create a new workspace
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(WorkspaceDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<WorkspaceDto>> Create([FromBody] CreateWorkspaceDto dto)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(dto.Name))
            {
                return BadRequest(new { message = "Workspace name is required." });
            }

            var userId = GetAuthenticatedUserId();
            var command = new CreateWorkspaceCommand(dto.Name, userId);
            var workspace = await _mediator.Send(command);
            return CreatedAtAction(nameof(GetById), new { id = workspace.Id }, workspace);
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
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
    /// Update workspace name
    /// </summary>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(WorkspaceDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<WorkspaceDto>> Update(Guid id, [FromBody] UpdateWorkspaceDto dto)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(dto.Name))
            {
                return BadRequest(new { message = "Workspace name is required." });
            }

            var userId = GetAuthenticatedUserId();
            var command = new UpdateWorkspaceCommand(id, dto.Name, userId);
            var workspace = await _mediator.Send(command);

            if (workspace == null)
            {
                return NotFound(new { message = "Workspace not found or you don't have permission to update it." });
            }

            return Ok(workspace);
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
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
    /// Delete workspace (cascades to all associated chat histories, messages, and PDFs)
    /// </summary>
    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> Delete(Guid id)
    {
        try
        {
            var userId = GetAuthenticatedUserId();
            var command = new DeleteWorkspaceCommand(id, userId);
            var result = await _mediator.Send(command);

            if (!result)
            {
                return NotFound(new { message = "Workspace not found or you don't have permission to delete it." });
            }

            return NoContent();
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
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
