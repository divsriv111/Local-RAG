using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Workspaces.Commands;

public class CreateWorkspaceCommandHandler : IRequestHandler<CreateWorkspaceCommand, WorkspaceDto>
{
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateWorkspaceCommandHandler(IRepository<Workspace> workspaceRepository, IUnitOfWork unitOfWork)
    {
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<WorkspaceDto> Handle(CreateWorkspaceCommand request, CancellationToken cancellationToken)
    {
        var workspace = new Workspace
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            UserId = request.UserId,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        await _workspaceRepository.AddAsync(workspace, cancellationToken);
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
