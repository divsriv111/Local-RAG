using Application.DTOs;
using Application.Interfaces;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Authentication.Commands;

public record RefreshTokenCommand(RefreshTokenRequest Request) : IRequest<(bool Success, string Message, TokenResponse? Token)>;

public class RefreshTokenCommandHandler : IRequestHandler<RefreshTokenCommand, (bool Success, string Message, TokenResponse? Token)>
{
    private readonly IRepository<User> _userRepository;
    private readonly IRepository<RefreshToken> _refreshTokenRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IJwtTokenService _jwtTokenService;

    public RefreshTokenCommandHandler(
        IRepository<User> userRepository,
        IRepository<RefreshToken> refreshTokenRepository,
        IUnitOfWork unitOfWork,
        IJwtTokenService jwtTokenService)
    {
        _userRepository = userRepository;
        _refreshTokenRepository = refreshTokenRepository;
        _unitOfWork = unitOfWork;
        _jwtTokenService = jwtTokenService;
    }

    public async Task<(bool Success, string Message, TokenResponse? Token)> Handle(
        RefreshTokenCommand request,
        CancellationToken cancellationToken)
    {
        try
        {
            // Find refresh token
            var refreshTokens = await _refreshTokenRepository.GetAllAsync();
            var refreshToken = refreshTokens.FirstOrDefault(rt => rt.Token == request.Request.RefreshToken);

            if (refreshToken == null)
            {
                return (false, "Invalid refresh token.", null);
            }

            // Check if token is revoked or expired
            if (refreshToken.IsRevoked)
            {
                return (false, "Refresh token has been revoked.", null);
            }

            if (refreshToken.ExpiresAt < DateTime.UtcNow)
            {
                return (false, "Refresh token has expired.", null);
            }

            // Get user
            var user = await _userRepository.GetByIdAsync(refreshToken.UserId);
            if (user == null)
            {
                return (false, "User not found.", null);
            }

            // Revoke old refresh token
            refreshToken.IsRevoked = true;
            refreshToken.RevokedAt = DateTime.UtcNow;
            await _refreshTokenRepository.UpdateAsync(refreshToken);

            // Generate new tokens
            var accessToken = _jwtTokenService.GenerateAccessToken(user);
            var newRefreshTokenValue = _jwtTokenService.GenerateRefreshToken();
            var newRefreshTokenExpiresAt = DateTime.UtcNow.AddDays(7);

            var newRefreshToken = new RefreshToken
            {
                Id = Guid.NewGuid(),
                Token = newRefreshTokenValue,
                UserId = user.Id,
                ExpiresAt = newRefreshTokenExpiresAt,
                CreatedAt = DateTime.UtcNow,
                IsRevoked = false
            };

            await _refreshTokenRepository.AddAsync(newRefreshToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            var tokenResponse = new TokenResponse(
                accessToken,
                newRefreshTokenValue,
                newRefreshTokenExpiresAt
            );

            return (true, "Token refreshed successfully.", tokenResponse);
        }
        catch (Exception ex)
        {
            return (false, $"An error occurred: {ex.Message}", null);
        }
    }
}
