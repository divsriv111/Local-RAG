using Application.DTOs;
using MediatR;

namespace Application.Features.Workspaces.Queries;

public record GetWorkspaceByIdQuery(Guid Id, Guid UserId) : IRequest<WorkspaceDetailDto?>;
