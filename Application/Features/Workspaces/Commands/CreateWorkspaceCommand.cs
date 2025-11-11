using Application.DTOs;
using MediatR;

namespace Application.Features.Workspaces.Commands;

public record CreateWorkspaceCommand(string Name, Guid UserId) : IRequest<WorkspaceDto>;
