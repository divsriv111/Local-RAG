using Application.DTOs;
using Application.Features.Workspaces.Commands;
using Application.Features.Workspaces.Queries;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class WorkspacesController : ControllerBase
{
    private readonly IMediator _mediator;

    public WorkspacesController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<WorkspaceDto>>> GetAll([FromQuery] string? search = null)
    {
        // TODO: Get UserId from authenticated user
        var userId = Guid.NewGuid(); // Placeholder
        var query = new GetAllWorkspacesQuery(userId, search);
        var workspaces = await _mediator.Send(query);
        return Ok(workspaces);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<WorkspaceDetailDto>> GetById(Guid id)
    {
        // TODO: Get UserId from authenticated user
        var userId = Guid.NewGuid(); // Placeholder
        var query = new GetWorkspaceByIdQuery(id, userId);
        var workspace = await _mediator.Send(query);

        if (workspace == null)
            return NotFound();

        return Ok(workspace);
    }

    [HttpPost]
    public async Task<ActionResult<WorkspaceDto>> Create([FromBody] CreateWorkspaceDto dto)
    {
        // TODO: Get UserId from authenticated user
        var userId = Guid.NewGuid(); // Placeholder
        var command = new CreateWorkspaceCommand(dto.Name, userId);
        var workspace = await _mediator.Send(command);
        return CreatedAtAction(nameof(GetById), new { id = workspace.Id }, workspace);
    }

    [HttpPut("{id}")]
    public async Task<ActionResult<WorkspaceDto>> Update(Guid id, [FromBody] UpdateWorkspaceDto dto)
    {
        // TODO: Implement update command
        return NoContent();
    }

    [HttpDelete("{id}")]
    public async Task<ActionResult> Delete(Guid id)
    {
        // TODO: Implement delete command
        return NoContent();
    }
}
