using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Authentication.Commands;

public record LogoutCommand(Guid UserId) : IRequest<(bool Success, string Message)>;

public class LogoutCommandHandler : IRequestHandler<LogoutCommand, (bool Success, string Message)>
{
    private readonly IRepository<RefreshToken> _refreshTokenRepository;
    private readonly IUnitOfWork _unitOfWork;

    public LogoutCommandHandler(
        IRepository<RefreshToken> refreshTokenRepository,
        IUnitOfWork unitOfWork)
    {
        _refreshTokenRepository = refreshTokenRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<(bool Success, string Message)> Handle(
        LogoutCommand request,
        CancellationToken cancellationToken)
    {
        try
        {
            // Get all active refresh tokens for the user
            var refreshTokens = await _refreshTokenRepository.GetAllAsync();
            var userTokens = refreshTokens
                .Where(rt => rt.UserId == request.UserId && !rt.IsRevoked)
                .ToList();

            if (!userTokens.Any())
            {
                return (true, "User already logged out.");
            }

            // Revoke all active tokens
            foreach (var token in userTokens)
            {
                token.IsRevoked = true;
                token.RevokedAt = DateTime.UtcNow;
                await _refreshTokenRepository.UpdateAsync(token);
            }

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            return (true, "Logged out successfully.");
        }
        catch (Exception ex)
        {
            return (false, $"An error occurred: {ex.Message}");
        }
    }
}
