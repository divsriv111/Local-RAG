using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Workspaces.Commands;

public class UpdateWorkspaceCommandHandler : IRequestHandler<UpdateWorkspaceCommand, WorkspaceDto?>
{
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;

    public UpdateWorkspaceCommandHandler(IRepository<Workspace> workspaceRepository, IUnitOfWork unitOfWork)
    {
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<WorkspaceDto?> Handle(UpdateWorkspaceCommand request, CancellationToken cancellationToken)
    {
        var workspace = await _workspaceRepository.GetByIdAsync(request.Id, cancellationToken);

        if (workspace == null)
            return null;

        // Validate user ownership
        if (workspace.UserId != request.UserId)
            return null;

        workspace.Name = request.Name;
        workspace.UpdatedAt = DateTime.UtcNow;

        await _workspaceRepository.UpdateAsync(workspace, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return new WorkspaceDto
        {
            Id = workspace.Id,
            Name = workspace.Name,
            UserId = workspace.UserId,
            CreatedAt = workspace.CreatedAt,
            UpdatedAt = workspace.UpdatedAt
        };
    }
}
