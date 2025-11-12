using Application.DTOs;
using MediatR;

namespace Application.Features.ChatHistories.Commands;

public record ArchiveChatHistoryCommand(Guid ChatHistoryId, Guid UserId) : IRequest<ChatHistoryDto>;
