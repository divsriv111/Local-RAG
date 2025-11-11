using Application.DTOs;
using Application.Interfaces;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Authentication.Commands;

public record LoginCommand(LoginRequest Request) : IRequest<(bool Success, string Message, TokenResponse? Token)>;

public class LoginCommandHandler : IRequestHandler<LoginCommand, (bool Success, string Message, TokenResponse? Token)>
{
    private readonly IRepository<User> _userRepository;
    private readonly IRepository<RefreshToken> _refreshTokenRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IJwtTokenService _jwtTokenService;
    private readonly IPasswordHasher _passwordHasher;

    public LoginCommandHandler(
        IRepository<User> userRepository,
        IRepository<RefreshToken> refreshTokenRepository,
        IUnitOfWork unitOfWork,
        IJwtTokenService jwtTokenService,
        IPasswordHasher passwordHasher)
    {
        _userRepository = userRepository;
        _refreshTokenRepository = refreshTokenRepository;
        _unitOfWork = unitOfWork;
        _jwtTokenService = jwtTokenService;
        _passwordHasher = passwordHasher;
    }

    public async Task<(bool Success, string Message, TokenResponse? Token)> Handle(
        LoginCommand request,
        CancellationToken cancellationToken)
    {
        try
        {
            // Find user by email
            var users = await _userRepository.GetAllAsync();
            var user = users.FirstOrDefault(u => u.Email == request.Request.Email);

            if (user == null)
            {
                return (false, "Invalid email or password.", null);
            }

            // Verify password
            if (!_passwordHasher.VerifyPassword(request.Request.Password, user.PasswordHash))
            {
                return (false, "Invalid email or password.", null);
            }

            // Generate tokens
            var accessToken = _jwtTokenService.GenerateAccessToken(user);
            var refreshTokenValue = _jwtTokenService.GenerateRefreshToken();
            var refreshTokenExpiresAt = DateTime.UtcNow.AddDays(7); // 7 days

            var refreshToken = new RefreshToken
            {
                Id = Guid.NewGuid(),
                Token = refreshTokenValue,
                UserId = user.Id,
                ExpiresAt = refreshTokenExpiresAt,
                CreatedAt = DateTime.UtcNow,
                IsRevoked = false
            };

            await _refreshTokenRepository.AddAsync(refreshToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            var tokenResponse = new TokenResponse(
                accessToken,
                refreshTokenValue,
                refreshTokenExpiresAt
            );

            return (true, "Login successful.", tokenResponse);
        }
        catch (Exception ex)
        {
            return (false, $"An error occurred: {ex.Message}", null);
        }
    }
}
