using Application.DTOs;
using MediatR;

namespace Application.Features.ChatHistories.Commands;

public record CreateChatHistoryCommand(Guid WorkspaceId, Guid UserId) : IRequest<ChatHistoryDto>;
