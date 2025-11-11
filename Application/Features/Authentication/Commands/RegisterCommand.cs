using Application.DTOs;
using Application.Interfaces;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Authentication.Commands;

public record RegisterCommand(RegisterRequest Request) : IRequest<(bool Success, string Message, TokenResponse? Token)>;

public class RegisterCommandHandler : IRequestHandler<RegisterCommand, (bool Success, string Message, TokenResponse? Token)>
{
    private readonly IRepository<User> _userRepository;
    private readonly IRepository<RefreshToken> _refreshTokenRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IJwtTokenService _jwtTokenService;
    private readonly IPasswordHasher _passwordHasher;

    public RegisterCommandHandler(
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
        RegisterCommand request,
        CancellationToken cancellationToken)
    {
        try
        {
            // Check if user already exists
            var existingUser = await _userRepository.GetAllAsync();
            if (existingUser.Any(u => u.Email == request.Request.Email))
            {
                return (false, "Email is already registered.", null);
            }

            if (existingUser.Any(u => u.Username == request.Request.Username))
            {
                return (false, "Username is already taken.", null);
            }

            // Create new user
            var user = new User
            {
                Id = Guid.NewGuid(),
                Username = request.Request.Username,
                Email = request.Request.Email,
                PasswordHash = _passwordHasher.HashPassword(request.Request.Password),
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            await _userRepository.AddAsync(user);

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

            return (true, "User registered successfully.", tokenResponse);
        }
        catch (Exception ex)
        {
            return (false, $"An error occurred: {ex.Message}", null);
        }
    }
}
