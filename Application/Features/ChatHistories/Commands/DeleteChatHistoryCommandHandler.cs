using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.ChatHistories.Commands;

public class DeleteChatHistoryCommandHandler : IRequestHandler<DeleteChatHistoryCommand, bool>
{
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IRepository<Message> _messageRepository;
    private readonly IUnitOfWork _unitOfWork;

    public DeleteChatHistoryCommandHandler(
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

    public async Task<bool> Handle(DeleteChatHistoryCommand request, CancellationToken cancellationToken)
    {
        var chatHistory = await _chatHistoryRepository.GetByIdAsync(request.ChatHistoryId, cancellationToken);

        if (chatHistory == null)
        {
            return false;
        }

        var workspace = await _workspaceRepository.GetByIdAsync(chatHistory.WorkspaceId, cancellationToken);

        if (workspace == null || workspace.UserId != request.UserId)
        {
            return false;
        }

        // Delete all messages first (cascade)
        var allMessages = await _messageRepository.GetAllAsync(cancellationToken);
        var messages = allMessages.Where(m => m.ChatHistoryId == chatHistory.Id).ToList();

        foreach (var message in messages)
        {
            _messageRepository.Delete(message);
        }

        // Delete the chat history
        _chatHistoryRepository.Delete(chatHistory);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return true;
    }
}
