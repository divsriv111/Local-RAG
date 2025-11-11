namespace Application.DTOs;

public record RegisterRequest(
    string Username,
    string Email,
    string Password);

public record LoginRequest(
    string Email,
    string Password);

public record TokenResponse(
    string AccessToken,
    string RefreshToken,
    DateTime ExpiresAt);

public record RefreshTokenRequest(
    string RefreshToken);

public record UpdateProfileRequest(
    string? Username,
    string? Email);

public record UserProfileResponse(
    Guid Id,
    string Username,
    string Email,
    DateTime CreatedAt,
    DateTime UpdatedAt);
