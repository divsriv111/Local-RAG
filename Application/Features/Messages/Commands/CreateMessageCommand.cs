using Application.DTOs;
using MediatR;

namespace Application.Features.Messages.Commands;

public record CreateMessageCommand(
    Guid ChatHistoryId,
    Guid UserId,
    string Content,
    bool IsUserMessage,
    string? References) : IRequest<MessageDto>;
