using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Workspaces.Queries;

public class GetAllWorkspacesQueryHandler : IRequestHandler<GetAllWorkspacesQuery, IEnumerable<WorkspaceDto>>
{
    private readonly IRepository<Workspace> _workspaceRepository;

    public GetAllWorkspacesQueryHandler(IRepository<Workspace> workspaceRepository)
    {
        _workspaceRepository = workspaceRepository;
    }

    public async Task<IEnumerable<WorkspaceDto>> Handle(GetAllWorkspacesQuery request, CancellationToken cancellationToken)
    {
        var workspaces = await _workspaceRepository.GetAllAsync(cancellationToken);

        var filteredWorkspaces = workspaces
            .Where(w => w.UserId == request.UserId);

        // Search functionality - case-insensitive search by workspace name
        if (!string.IsNullOrWhiteSpace(request.SearchTerm))
        {
            filteredWorkspaces = filteredWorkspaces
                .Where(w => w.Name.Contains(request.SearchTerm, StringComparison.OrdinalIgnoreCase));
        }

        // Sorting
        var sortedWorkspaces = request.SortBy.ToLower() switch
        {
            "name" => request.SortOrder.ToLower() == "asc"
                ? filteredWorkspaces.OrderBy(w => w.Name)
                : filteredWorkspaces.OrderByDescending(w => w.Name),
            "updatedat" => request.SortOrder.ToLower() == "asc"
                ? filteredWorkspaces.OrderBy(w => w.UpdatedAt)
                : filteredWorkspaces.OrderByDescending(w => w.UpdatedAt),
            _ => request.SortOrder.ToLower() == "asc"
                ? filteredWorkspaces.OrderBy(w => w.CreatedAt)
                : filteredWorkspaces.OrderByDescending(w => w.CreatedAt)
        };

        return sortedWorkspaces
            .Select(w => new WorkspaceDto
            {
                Id = w.Id,
                Name = w.Name,
                UserId = w.UserId,
                CreatedAt = w.CreatedAt,
                UpdatedAt = w.UpdatedAt
            });
    }
}
