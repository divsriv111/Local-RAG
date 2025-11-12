using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.ChatHistories.Commands;

public class CreateChatHistoryCommandHandler : IRequestHandler<CreateChatHistoryCommand, ChatHistoryDto>
{
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateChatHistoryCommandHandler(
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Workspace> workspaceRepository,
        IUnitOfWork unitOfWork)
    {
        _chatHistoryRepository = chatHistoryRepository;
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatHistoryDto> Handle(CreateChatHistoryCommand request, CancellationToken cancellationToken)
    {
        // Verify workspace exists and user owns it
        var workspace = await _workspaceRepository.GetByIdAsync(request.WorkspaceId, cancellationToken);
        if (workspace == null || workspace.UserId != request.UserId)
        {
            throw new UnauthorizedAccessException("Workspace not found or access denied.");
        }

        var chatHistory = new ChatHistory
        {
            Id = Guid.NewGuid(),
            WorkspaceId = request.WorkspaceId,
            Name = "New Chat", // Default name, will be updated with first query
            FirstQuery = string.Empty,
            CreatedAt = DateTime.UtcNow,
            IsArchived = false
        };

        await _chatHistoryRepository.AddAsync(chatHistory, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return new ChatHistoryDto
        {
            Id = chatHistory.Id,
            WorkspaceId = chatHistory.WorkspaceId,
            Name = chatHistory.Name,
            FirstQuery = chatHistory.FirstQuery,
            CreatedAt = chatHistory.CreatedAt,
            IsArchived = chatHistory.IsArchived,
            MessageCount = 0
        };
    }
}
