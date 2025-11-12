using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Messages.Queries;

public class GetMessagesByChatHistoryQueryHandler
    : IRequestHandler<GetMessagesByChatHistoryQuery, PaginatedMessagesDto>
{
    private readonly IRepository<Message> _messageRepository;
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;

    public GetMessagesByChatHistoryQueryHandler(
        IRepository<Message> messageRepository,
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Workspace> workspaceRepository)
    {
        _messageRepository = messageRepository;
        _chatHistoryRepository = chatHistoryRepository;
        _workspaceRepository = workspaceRepository;
    }

    public async Task<PaginatedMessagesDto> Handle(
        GetMessagesByChatHistoryQuery request,
        CancellationToken cancellationToken)
    {
        // Verify chat history exists and user owns it
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

        var allMessages = await _messageRepository.GetAllAsync(cancellationToken);
        var chatMessages = allMessages
            .Where(m => m.ChatHistoryId == request.ChatHistoryId)
            .OrderBy(m => m.Timestamp)
            .ToList();

        var totalCount = chatMessages.Count;
        var totalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize);

        var paginatedMessages = chatMessages
            .Skip((request.PageNumber - 1) * request.PageSize)
            .Take(request.PageSize)
            .Select(m => new MessageDto
            {
                Id = m.Id,
                ChatHistoryId = m.ChatHistoryId,
                Content = m.Content,
                IsUserMessage = m.IsUserMessage,
                Timestamp = m.Timestamp,
                References = m.References
            })
            .ToList();

        return new PaginatedMessagesDto
        {
            Messages = paginatedMessages,
            TotalCount = totalCount,
            PageNumber = request.PageNumber,
            PageSize = request.PageSize,
            TotalPages = totalPages
        };
    }
}
