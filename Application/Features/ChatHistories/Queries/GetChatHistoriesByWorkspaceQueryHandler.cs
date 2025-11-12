using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.ChatHistories.Queries;

public class GetChatHistoriesByWorkspaceQueryHandler
    : IRequestHandler<GetChatHistoriesByWorkspaceQuery, IEnumerable<ChatHistoryListItemDto>>
{
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IRepository<Message> _messageRepository;

    public GetChatHistoriesByWorkspaceQueryHandler(
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Workspace> workspaceRepository,
        IRepository<Message> messageRepository)
    {
        _chatHistoryRepository = chatHistoryRepository;
        _workspaceRepository = workspaceRepository;
        _messageRepository = messageRepository;
    }

    public async Task<IEnumerable<ChatHistoryListItemDto>> Handle(
        GetChatHistoriesByWorkspaceQuery request,
        CancellationToken cancellationToken)
    {
        // Verify workspace exists and user owns it
        var workspace = await _workspaceRepository.GetByIdAsync(request.WorkspaceId, cancellationToken);
        if (workspace == null || workspace.UserId != request.UserId)
        {
            throw new UnauthorizedAccessException("Workspace not found or access denied.");
        }

        var allChatHistories = await _chatHistoryRepository.GetAllAsync(cancellationToken);
        var allMessages = await _messageRepository.GetAllAsync(cancellationToken);

        var chatHistories = allChatHistories
            .Where(ch => ch.WorkspaceId == request.WorkspaceId);

        if (!request.IncludeArchived)
        {
            chatHistories = chatHistories.Where(ch => !ch.IsArchived);
        }

        var result = chatHistories
            .OrderByDescending(ch => ch.CreatedAt)
            .Select(ch => new ChatHistoryListItemDto
            {
                Id = ch.Id,
                Name = ch.Name,
                CreatedAt = ch.CreatedAt,
                IsArchived = ch.IsArchived,
                MessageCount = allMessages.Count(m => m.ChatHistoryId == ch.Id)
            })
            .ToList();

        return result;
    }
}
