using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.ChatHistories.Commands;

public class ArchiveChatHistoryCommandHandler : IRequestHandler<ArchiveChatHistoryCommand, ChatHistoryDto>
{
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IRepository<Message> _messageRepository;
    private readonly IUnitOfWork _unitOfWork;

    public ArchiveChatHistoryCommandHandler(
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Workspace> workspaceRepository,
        IRepository<Message> messageRepository,
        IUnitOfWork unitOfWork)
    {
        _chatHistoryRepository = chatHistoryRepository;
        _workspaceRepository = workspaceRepository;
        _messageRepository = messageRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<ChatHistoryDto> Handle(ArchiveChatHistoryCommand request, CancellationToken cancellationToken)
    {
        var chatHistory = await _chatHistoryRepository.GetByIdAsync(request.ChatHistoryId, cancellationToken);

        if (chatHistory == null)
        {
            throw new UnauthorizedAccessException("Chat history not found or access denied.");
        }

        var workspace = await _workspaceRepository.GetByIdAsync(chatHistory.WorkspaceId, cancellationToken);

        if (workspace == null || workspace.UserId != request.UserId)
        {
            throw new UnauthorizedAccessException("Chat history not found or access denied.");
        }

        var messages = await _messageRepository.GetAllAsync(cancellationToken);
        var messageCount = messages.Count(m => m.ChatHistoryId == chatHistory.Id);

        chatHistory.IsArchived = true;
        _chatHistoryRepository.Update(chatHistory);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return new ChatHistoryDto
        {
            Id = chatHistory.Id,
            WorkspaceId = chatHistory.WorkspaceId,
            Name = chatHistory.Name,
            FirstQuery = chatHistory.FirstQuery,
            CreatedAt = chatHistory.CreatedAt,
            IsArchived = chatHistory.IsArchived,
            MessageCount = messageCount
        };
    }
}
