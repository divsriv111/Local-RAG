using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Authentication.Commands;

public record UpdateProfileCommand(Guid UserId, UpdateProfileRequest Request)
    : IRequest<(bool Success, string Message, UserProfileResponse? Profile)>;

public class UpdateProfileCommandHandler
    : IRequestHandler<UpdateProfileCommand, (bool Success, string Message, UserProfileResponse? Profile)>
{
    private readonly IRepository<User> _userRepository;
    private readonly IUnitOfWork _unitOfWork;

    public UpdateProfileCommandHandler(
        IRepository<User> userRepository,
        IUnitOfWork unitOfWork)
    {
        _userRepository = userRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<(bool Success, string Message, UserProfileResponse? Profile)> Handle(
        UpdateProfileCommand request,
        CancellationToken cancellationToken)
    {
        try
        {
            // Get user
            var user = await _userRepository.GetByIdAsync(request.UserId);
            if (user == null)
            {
                return (false, "User not found.", null);
            }

            var allUsers = await _userRepository.GetAllAsync();

            // Update username if provided
            if (!string.IsNullOrEmpty(request.Request.Username))
            {
                // Check if username is taken by another user
                if (allUsers.Any(u => u.Username == request.Request.Username && u.Id != user.Id))
                {
                    return (false, "Username is already taken.", null);
                }
                user.Username = request.Request.Username;
            }

            // Update email if provided
            if (!string.IsNullOrEmpty(request.Request.Email))
            {
                // Check if email is taken by another user
                if (allUsers.Any(u => u.Email == request.Request.Email && u.Id != user.Id))
                {
                    return (false, "Email is already registered.", null);
                }
                user.Email = request.Request.Email;
            }

            user.UpdatedAt = DateTime.UtcNow;
            await _userRepository.UpdateAsync(user);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            var profileResponse = new UserProfileResponse(
                user.Id,
                user.Username,
                user.Email,
                user.CreatedAt,
                user.UpdatedAt
            );

            return (true, "Profile updated successfully.", profileResponse);
        }
        catch (Exception ex)
        {
            return (false, $"An error occurred: {ex.Message}", null);
        }
    }
}
