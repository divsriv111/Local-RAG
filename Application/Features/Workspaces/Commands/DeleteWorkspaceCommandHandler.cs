using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Workspaces.Commands;

public class DeleteWorkspaceCommandHandler : IRequestHandler<DeleteWorkspaceCommand, bool>
{
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;

    public DeleteWorkspaceCommandHandler(IRepository<Workspace> workspaceRepository, IUnitOfWork unitOfWork)
    {
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<bool> Handle(DeleteWorkspaceCommand request, CancellationToken cancellationToken)
    {
        var workspace = await _workspaceRepository.GetByIdAsync(request.Id, cancellationToken);

        if (workspace == null)
            return false;

        // Validate user ownership
        if (workspace.UserId != request.UserId)
            return false;

        // Cascade delete is configured in the database model
        // When workspace is deleted, all related ChatHistories, Messages, and PDFDocuments will be deleted
        await _workspaceRepository.DeleteAsync(workspace, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return true;
    }
}
