using Application.DTOs;
using MediatR;

namespace Application.Features.Workspaces.Queries;

public record GetAllWorkspacesQuery(Guid UserId, string? SearchTerm = null) : IRequest<IEnumerable<WorkspaceDto>>;
