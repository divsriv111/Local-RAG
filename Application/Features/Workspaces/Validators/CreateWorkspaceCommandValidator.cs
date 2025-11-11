using Application.DTOs;
using FluentValidation;

namespace Application.Features.Workspaces.Validators;

public class CreateWorkspaceCommandValidator : AbstractValidator<CreateWorkspaceDto>
{
    public CreateWorkspaceCommandValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Workspace name is required")
            .MaximumLength(100).WithMessage("Workspace name cannot exceed 100 characters");
    }
}
