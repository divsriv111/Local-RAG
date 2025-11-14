# Profile Component - Quick Start

## 🚀 5-Minute Setup

### 1. Verify Installation (30 seconds)

```bash
# Check if PrimeNG is installed
npm list primeng primeicons

# If not installed, run:
npm install primeng primeicons
```

### 2. Add Route (1 minute)

In `app-routing.module.ts`:

```typescript
{
  path: 'profile',
  loadChildren: () => import('./features/profile/profile.module').then(m => m.ProfileModule),
  canActivate: [AuthGuard]
}
```

### 3. Add Navigation Link (30 seconds)

In your navbar component:

```html
<a routerLink="/profile" class="nav-link"> <i class="pi pi-user"></i> Profile </a>
```

### 4. Backend API - Copy & Paste (2 minutes)

#### Create `Controllers/UsersController.cs`:

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

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
        return Ok(user);
    }

    [HttpPut("profile")]
    public async Task<ActionResult<UserDto>> UpdateProfile([FromBody] UpdateUserDTO dto)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var user = await _userService.UpdateProfileAsync(userId, dto);
        return Ok(user);
    }

    [HttpPost("change-password")]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordDTO dto)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        await _userService.ChangePasswordAsync(userId, dto.CurrentPassword, dto.NewPassword);
        return NoContent();
    }
}
```

### 5. Test (1 minute)

```bash
# Terminal 1 - Backend
cd backend
dotnet run

# Terminal 2 - Frontend
cd rag-chatbot-frontend
ng serve

# Open browser
# Navigate to: http://localhost:4200/profile
```

## ✅ Done!

Your profile component is now ready to use.

---

## 📖 Need More Details?

- **Full Documentation**: See `PROFILE_README.md`
- **Integration Guide**: See `PROFILE_INTEGRATION_GUIDE.md`
- **Implementation Summary**: See `PROFILE_IMPLEMENTATION_SUMMARY.md`

## 🆘 Having Issues?

### Common Fix #1: Styles Not Loading

Add to `angular.json`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css"
]
```

### Common Fix #2: CORS Error

Add to backend `Program.cs`:

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
        policy.WithOrigins("http://localhost:4200")
              .AllowAnyMethod()
              .AllowAnyHeader());
});

app.UseCors("AllowAngular");
```

### Common Fix #3: Toast Not Showing

Ensure `<p-toast>` is in `profile.component.html` (already added)

---

**That's it! You're ready to go! 🎉**
