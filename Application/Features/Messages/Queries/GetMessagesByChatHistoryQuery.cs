using Application.DTOs;
using MediatR;

namespace Application.Features.Messages.Queries;

public record GetMessagesByChatHistoryQuery(
    Guid ChatHistoryId,
    Guid UserId,
    int PageNumber = 1,
    int PageSize = 50) : IRequest<PaginatedMessagesDto>;
