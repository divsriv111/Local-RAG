using Application.DTOs;
using MediatR;

namespace Application.Features.Workspaces.Commands;

public record UpdateWorkspaceCommand(Guid Id, string Name, Guid UserId) : IRequest<WorkspaceDto?>;
