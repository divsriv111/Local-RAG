# Profile Management Component

A complete user profile management component with profile editing and password change functionality.

## Features

✅ **Profile Information**

- Display current user information (username, email)
- Edit username and email with validation
- Real-time form validation
- Cancel changes to revert to original values

✅ **Password Management**

- Collapsible password change section
- Current password verification
- Password strength validation (min 8 chars, 1 uppercase, 1 number, 1 special char)
- Password confirmation with match validation
- Real-time password strength feedback

✅ **User Experience**

- Responsive design using Bootstrap grid
- PrimeNG components for consistent UI
- Loading states and progress indicators
- Toast notifications for success/error messages
- Field-level error messages
- Accessible form controls

## Files Created

```
src/app/
├── core/
│   ├── models/
│   │   └── user.model.ts              # User and DTO interfaces
│   └── services/
│       └── profile.service.ts          # Profile API service
└── features/
    └── profile/
        ├── profile.component.ts        # Component logic
        ├── profile.component.html      # Component template
        ├── profile.component.scss      # Component styles
        └── profile.module.ts           # Feature module
```

## Installation

### 1. Install Required PrimeNG Modules

Make sure the following PrimeNG modules are installed:

```bash
npm install primeng primeicons
```

### 2. Import in App Module

If not using lazy loading, import the ProfileModule in your app module:

```typescript
import { ProfileModule } from './features/profile/profile.module';

@NgModule({
  imports: [
    // ... other imports
    ProfileModule,
  ],
})
export class AppModule {}
```

### 3. Add Route

Add the profile route to your routing configuration:

```typescript
const routes: Routes = [
  {
    path: 'profile',
    loadChildren: () => import('./features/profile/profile.module').then((m) => m.ProfileModule),
    canActivate: [AuthGuard], // Optional: Add authentication guard
  },
];
```

## Usage

### Navigation

Navigate to the profile page:

```typescript
this.router.navigate(['/profile']);
```

Or add a link in your navigation:

```html
<a routerLink="/profile">Profile</a>
```

### API Endpoints Required

The component expects the following API endpoints to be available:

**GET** `/api/users/profile`

- Returns current user information
- Response: `User` object

**PUT** `/api/users/profile`

- Updates user profile (username, email)
- Request body: `UpdateUserDTO { username: string, email: string }`
- Response: Updated `User` object

**POST** `/api/users/change-password`

- Changes user password
- Request body: `{ currentPassword: string, newPassword: string }`
- Response: `void` (204 No Content)

### Backend API Implementation Example

```csharp
[HttpGet("profile")]
[Authorize]
public async Task<ActionResult<UserDto>> GetProfile()
{
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    var user = await _userService.GetByIdAsync(userId);
    return Ok(user);
}

[HttpPut("profile")]
[Authorize]
public async Task<ActionResult<UserDto>> UpdateProfile([FromBody] UpdateUserDTO dto)
{
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    var user = await _userService.UpdateProfileAsync(userId, dto);
    return Ok(user);
}

[HttpPost("change-password")]
[Authorize]
public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordDTO dto)
{
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    await _userService.ChangePasswordAsync(userId, dto.CurrentPassword, dto.NewPassword);
    return NoContent();
}
```

## Component API

### ProfileComponent

**Properties:**

- `profileForm: FormGroup` - Reactive form for profile information
- `passwordForm: FormGroup` - Reactive form for password change
- `currentUser: User | null` - Current user data
- `isLoadingProfile: boolean` - Loading state for profile fetch
- `isUpdatingProfile: boolean` - Loading state for profile update
- `isChangingPassword: boolean` - Loading state for password change
- `passwordPanelCollapsed: boolean` - Password section collapse state

**Methods:**

- `loadProfile()` - Fetches current user profile
- `updateProfile()` - Updates user profile
- `cancelProfileChanges()` - Reverts form to original values
- `changePassword()` - Changes user password
- `cancelPasswordChange()` - Resets password form

### ProfileService

**Methods:**

- `getProfile(): Observable<User>` - Get current user profile
- `updateProfile(user: UpdateUserDTO): Observable<User>` - Update profile
- `changePassword(currentPassword: string, newPassword: string): Observable<void>` - Change password

## Validation Rules

### Profile Form

- **Username**: Required, 3-50 characters
- **Email**: Required, valid email format

### Password Form

- **Current Password**: Required
- **New Password**: Required, must contain:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 number
  - At least 1 special character
- **Confirm Password**: Required, must match new password

## Error Handling

### HTTP Status Codes

- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Wrong current password
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

### Error Messages

All errors are displayed using:

- **Toast notifications** for general success/error messages
- **Field-level errors** shown below input fields
- **Form-level errors** for password mismatch

## Customization

### Styling

Modify `profile.component.scss` to customize:

- Colors and theme
- Spacing and layout
- Button styles
- Card appearance

### Validation Rules

Update validators in `initializeForms()` method:

```typescript
this.profileForm = this.fb.group({
  username: ['', [Validators.required, Validators.minLength(3)]],
  email: ['', [Validators.required, Validators.email, customEmailValidator]],
});
```

### Additional Fields

To add more profile fields:

1. Update `User` interface in `user.model.ts`
2. Add form control in `initializeForms()`
3. Add input field in template
4. Update `UpdateUserDTO` interface

Example - Adding phone number:

```typescript
// user.model.ts
export interface User {
  // ... existing fields
  phoneNumber?: string;
}

// profile.component.ts
this.profileForm = this.fb.group({
  username: ['', [Validators.required]],
  email: ['', [Validators.required, Validators.email]],
  phoneNumber: ['', [Validators.pattern(/^\+?[1-9]\d{1,14}$/)]], // E.164 format
});

// profile.component.html
<div class="col-12 mb-4">
  <label for="phoneNumber" class="form-label">
    Phone Number
  </label>
  <input id="phoneNumber" type="tel" pInputText formControlName="phoneNumber" class="w-100" />
</div>;
```

## Accessibility

The component includes:

- Proper label associations with `for` attributes
- ARIA attributes for screen readers
- Keyboard navigation support
- Focus management
- Error announcements
- Required field indicators

## Testing

### Unit Tests Example

```typescript
describe('ProfileComponent', () => {
  let component: ProfileComponent;
  let fixture: ComponentFixture<ProfileComponent>;
  let profileService: jasmine.SpyObj<ProfileService>;

  beforeEach(() => {
    const profileServiceSpy = jasmine.createSpyObj('ProfileService', [
      'getProfile',
      'updateProfile',
      'changePassword',
    ]);

    TestBed.configureTestingModule({
      declarations: [ProfileComponent],
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      providers: [{ provide: ProfileService, useValue: profileServiceSpy }, MessageService],
    });

    fixture = TestBed.createComponent(ProfileComponent);
    component = fixture.componentInstance;
    profileService = TestBed.inject(ProfileService) as jasmine.SpyObj<ProfileService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load profile on init', () => {
    const mockUser = { id: '1', username: 'testuser', email: 'test@example.com' };
    profileService.getProfile.and.returnValue(of(mockUser));

    component.ngOnInit();

    expect(profileService.getProfile).toHaveBeenCalled();
    expect(component.currentUser).toEqual(mockUser);
  });

  it('should validate password strength', () => {
    component.ngOnInit();
    const passwordControl = component.passwordForm.get('newPassword');

    passwordControl?.setValue('weak');
    expect(passwordControl?.errors?.['passwordStrength']).toBeTruthy();

    passwordControl?.setValue('Strong@123');
    expect(passwordControl?.errors).toBeNull();
  });
});
```

## Troubleshooting

### Common Issues

**Issue: Forms not submitting**

- Ensure all required fields are filled
- Check browser console for validation errors
- Verify API endpoints are accessible

**Issue: Password validation not working**

- Check password requirements in error message
- Ensure special characters are allowed by backend
- Verify regex patterns match backend validation

**Issue: Toast messages not showing**

- Ensure `MessageService` is provided in module
- Add `<p-toast>` component to template
- Check console for errors

**Issue: Styles not applied**

- Verify PrimeNG CSS is imported in angular.json
- Check for CSS specificity conflicts
- Ensure Bootstrap is properly configured

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - Part of RAG Chatbot Application

## Support

For issues or questions:

- Check the main project README
- Review API documentation
- Create a GitHub issue
