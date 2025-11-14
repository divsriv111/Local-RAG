# Profile Component Integration Checklist

## ✅ Quick Setup Guide

### Step 1: Verify PrimeNG Installation

Check that PrimeNG and PrimeIcons are installed:

```bash
npm list primeng primeicons
```

If not installed:

```bash
npm install primeng primeicons
```

### Step 2: Update angular.json

Ensure these styles are in your `angular.json` under `projects.your-app.architect.build.options.styles`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css",
  "node_modules/bootstrap/dist/css/bootstrap.min.css",
  "src/styles.scss"
]
```

### Step 3: Add Routing

In your `app-routing.module.ts` or routing configuration:

```typescript
const routes: Routes = [
  // ... other routes
  {
    path: 'profile',
    loadChildren: () => import('./features/profile/profile.module').then((m) => m.ProfileModule),
    canActivate: [AuthGuard], // Add your auth guard
  },
];
```

### Step 4: Add Navigation Link

In your navigation component (e.g., `navbar.component.html`):

```html
<a routerLink="/profile" class="nav-link"> <i class="pi pi-user"></i> Profile </a>
```

Or using PrimeNG Menu:

```typescript
this.items = [
  {
    label: 'Profile',
    icon: 'pi pi-user',
    routerLink: '/profile',
  },
];
```

### Step 5: Backend API Implementation

Implement these endpoints in your ASP.NET Core API:

#### Controllers/UsersController.cs

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/users")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("profile")]
    public async Task<ActionResult<UserDto>> GetProfile()
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var user = await _userService.GetByIdAsync(userId);

        if (user == null)
            return NotFound();

        return Ok(user);
    }

    [HttpPut("profile")]
    public async Task<ActionResult<UserDto>> UpdateProfile([FromBody] UpdateUserDTO dto)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        try
        {
            var user = await _userService.UpdateProfileAsync(userId, dto);
            return Ok(user);
        }
        catch (ValidationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    [HttpPost("change-password")]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordDTO dto)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        try
        {
            await _userService.ChangePasswordAsync(userId, dto.CurrentPassword, dto.NewPassword);
            return NoContent();
        }
        catch (UnauthorizedException)
        {
            return Unauthorized(new { message = "Current password is incorrect" });
        }
        catch (ValidationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }
}
```

#### DTOs/UserDtos.cs

```csharp
public class UserDto
{
    public Guid Id { get; set; }
    public string Username { get; set; }
    public string Email { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

public class UpdateUserDTO
{
    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string Username { get; set; }

    [Required]
    [EmailAddress]
    public string Email { get; set; }
}

public class ChangePasswordDTO
{
    [Required]
    public string CurrentPassword { get; set; }

    [Required]
    [StringLength(100, MinimumLength = 8)]
    [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
        ErrorMessage = "Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character")]
    public string NewPassword { get; set; }
}
```

#### Services/UserService.cs

```csharp
public interface IUserService
{
    Task<UserDto> GetByIdAsync(string userId);
    Task<UserDto> UpdateProfileAsync(string userId, UpdateUserDTO dto);
    Task ChangePasswordAsync(string userId, string currentPassword, string newPassword);
}

public class UserService : IUserService
{
    private readonly ApplicationDbContext _context;
    private readonly IPasswordHasher<User> _passwordHasher;

    public UserService(ApplicationDbContext context, IPasswordHasher<User> passwordHasher)
    {
        _context = context;
        _passwordHasher = passwordHasher;
    }

    public async Task<UserDto> GetByIdAsync(string userId)
    {
        var user = await _context.Users.FindAsync(Guid.Parse(userId));

        if (user == null)
            throw new NotFoundException("User not found");

        return new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            CreatedAt = user.CreatedAt,
            UpdatedAt = user.UpdatedAt
        };
    }

    public async Task<UserDto> UpdateProfileAsync(string userId, UpdateUserDTO dto)
    {
        var user = await _context.Users.FindAsync(Guid.Parse(userId));

        if (user == null)
            throw new NotFoundException("User not found");

        // Check if username is already taken by another user
        if (await _context.Users.AnyAsync(u => u.Username == dto.Username && u.Id != user.Id))
            throw new ValidationException("Username is already taken");

        // Check if email is already taken by another user
        if (await _context.Users.AnyAsync(u => u.Email == dto.Email && u.Id != user.Id))
            throw new ValidationException("Email is already taken");

        user.Username = dto.Username;
        user.Email = dto.Email;
        user.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        return new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            CreatedAt = user.CreatedAt,
            UpdatedAt = user.UpdatedAt
        };
    }

    public async Task ChangePasswordAsync(string userId, string currentPassword, string newPassword)
    {
        var user = await _context.Users.FindAsync(Guid.Parse(userId));

        if (user == null)
            throw new NotFoundException("User not found");

        // Verify current password
        var result = _passwordHasher.VerifyHashedPassword(user, user.PasswordHash, currentPassword);

        if (result == PasswordVerificationResult.Failed)
            throw new UnauthorizedException("Current password is incorrect");

        // Hash new password
        user.PasswordHash = _passwordHasher.HashPassword(user, newPassword);
        user.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();
    }
}
```

### Step 6: Test the Integration

1. **Start the backend API**:

   ```bash
   cd backend
   dotnet run
   ```

2. **Start the Angular app**:

   ```bash
   cd rag-chatbot-frontend
   ng serve
   ```

3. **Navigate to profile page**:

   - Open browser: http://localhost:4200/profile
   - Log in if not authenticated
   - Verify profile loads correctly

4. **Test functionality**:
   - ✅ Update username
   - ✅ Update email
   - ✅ Change password
   - ✅ Cancel changes
   - ✅ Error handling (wrong password, invalid email)

## 🔍 Verification Checklist

- [ ] PrimeNG and Bootstrap CSS loaded in angular.json
- [ ] Profile route configured in routing module
- [ ] Backend API endpoints implemented and tested
- [ ] JWT authentication working
- [ ] Toast notifications appearing
- [ ] Form validations working
- [ ] Password strength indicator showing
- [ ] Responsive design on mobile devices
- [ ] Error messages displaying correctly
- [ ] Success messages showing on update

## 🐛 Troubleshooting

### Issue: "Cannot find module 'primeng/...'"

**Solution**: Install PrimeNG

```bash
npm install primeng primeicons
```

### Issue: Styles not applied

**Solution**: Check angular.json has PrimeNG styles, restart `ng serve`

### Issue: API returns 401

**Solution**: Verify JWT token in localStorage, check Authorization header in network tab

### Issue: CORS error

**Solution**: Add CORS policy in backend Program.cs:

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
    {
        policy.WithOrigins("http://localhost:4200")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

app.UseCors("AllowAngular");
```

### Issue: Toast not showing

**Solution**: Add `<p-toast>` to profile.component.html, ensure MessageService is provided

## 📚 Additional Resources

- [PrimeNG Documentation](https://primeng.org/)
- [Angular Reactive Forms](https://angular.io/guide/reactive-forms)
- [ASP.NET Core Web API](https://docs.microsoft.com/en-us/aspnet/core/web-api/)

## ✨ Next Steps

1. Add profile picture upload
2. Implement email verification
3. Add two-factor authentication
4. Create account deletion feature
5. Add activity log/audit trail

---

**Need Help?** Check the PROFILE_README.md for detailed documentation.
