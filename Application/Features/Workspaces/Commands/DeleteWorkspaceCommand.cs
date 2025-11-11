using MediatR;

namespace Application.Features.Workspaces.Commands;

public record DeleteWorkspaceCommand(Guid Id, Guid UserId) : IRequest<bool>;
