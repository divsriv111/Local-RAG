using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Messages.Commands;

public class CreateMessageCommandHandler : IRequestHandler<CreateMessageCommand, MessageDto>
{
    private readonly IRepository<Message> _messageRepository;
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateMessageCommandHandler(
        IRepository<Message> messageRepository,
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<Workspace> workspaceRepository,
        IUnitOfWork unitOfWork)
    {
        _messageRepository = messageRepository;
        _chatHistoryRepository = chatHistoryRepository;
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<MessageDto> Handle(CreateMessageCommand request, CancellationToken cancellationToken)
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

        var message = new Message
        {
            Id = Guid.NewGuid(),
            ChatHistoryId = request.ChatHistoryId,
            Content = request.Content,
            IsUserMessage = request.IsUserMessage,
            Timestamp = DateTime.UtcNow,
            References = request.References
        };

        await _messageRepository.AddAsync(message, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return new MessageDto
        {
            Id = message.Id,
            ChatHistoryId = message.ChatHistoryId,
            Content = message.Content,
            IsUserMessage = message.IsUserMessage,
            Timestamp = message.Timestamp,
            References = message.References
        };
    }
}
