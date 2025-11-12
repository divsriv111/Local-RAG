using MediatR;

namespace Application.Features.ChatHistories.Commands;

public record DeleteChatHistoryCommand(Guid ChatHistoryId, Guid UserId) : IRequest<bool>;
