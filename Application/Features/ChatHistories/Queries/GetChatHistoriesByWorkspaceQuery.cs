using Application.DTOs;
using MediatR;

namespace Application.Features.ChatHistories.Queries;

public record GetChatHistoriesByWorkspaceQuery(
    Guid WorkspaceId,
    Guid UserId,
    bool IncludeArchived = false) : IRequest<IEnumerable<ChatHistoryListItemDto>>;
