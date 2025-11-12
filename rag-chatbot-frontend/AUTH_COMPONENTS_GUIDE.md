# Authentication Components - Implementation Guide

This document describes the complete authentication system implemented for the RAG Chatbot Frontend using Angular, PrimeNG, and Bootstrap.

## Overview

The authentication system includes:

- **Login Component**: User authentication with JWT tokens
- **Register Component**: User registration with comprehensive validation
- **Auth Service**: Core authentication logic and token management
- **Auth Guard**: Route protection for authenticated-only pages
- **Auth Interceptor**: Automatic token injection and error handling

## Components

### 1. LoginComponent

**Location**: `src/app/features/auth/login/`

**Features**:

- PrimeNG Card, InputText, Password, and Button components
- Reactive forms with validation
- Username and password fields (both required)
- JWT token storage in localStorage
- Automatic navigation to `/workspaces` on success
- Error messages using PrimeNG Toast
- Responsive design with Bootstrap grid
- Loading spinner during authentication
- Session expired message handling from query params

**Usage**:

```typescript
// Navigate to login
this.router.navigate(['/auth/login']);

// With session expired message
this.router.navigate(['/auth/login'], {
  queryParams: { message: 'Session expired. Please login again.' },
});
```

### 2. RegisterComponent

**Location**: `src/app/features/auth/register/`

**Features**:

- Form fields: username (min 3 chars), email, password, confirmPassword
- **Password Strength Validator**: Requires uppercase, lowercase, number, and special character
- **Email Format Validation**: Standard email pattern validation
- **Passwords Match Validator**: Custom form-level validator
- Password strength meter with visual feedback
- Success message and automatic redirect to login
- PrimeNG InputText and Password components with toggle mask
- Real-time validation feedback

**Password Requirements**:

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&\*()\_+-=[]{}...etc)

### 3. AuthService

**Location**: `src/app/core/services/auth.service.ts`

**Methods**:

```typescript
// Login user
login(username: string, password: string): Observable<AuthResponse>

// Register new user
register(user: RegisterDTO): Observable<void>

// Logout user - clears tokens and navigates to login
logout(): void

// Check if user is authenticated and token is valid
isAuthenticated(): boolean

// Get current JWT token
getToken(): string | null

// Get current user information from API
getCurrentUser(): Observable<User>

// Observable stream of current user
currentUser$: Observable<User | null>
```

**Token Management**:

- Stores JWT token in localStorage as `access_token`
- Stores refresh token in localStorage as `refresh_token`
- Automatically checks token expiration using JWT payload
- Clears tokens on logout

**Integration**:

```typescript
// Inject the service
constructor(private authService: AuthService) {}

// Login
this.authService.login('username', 'password').subscribe({
  next: (response) => console.log('Login successful', response),
  error: (error) => console.error('Login failed', error)
});

// Check authentication status
if (this.authService.isAuthenticated()) {
  // User is logged in
}

// Subscribe to current user
this.authService.currentUser$.subscribe(user => {
  console.log('Current user:', user);
});
```

### 4. AuthGuard

**Location**: `src/app/core/guards/auth.guard.ts`

**Implementation**: Functional guard using `CanActivateFn`

**Features**:

- Implements `CanActivate` interface
- Redirects to `/auth/login` if not authenticated
- Preserves return URL in query params for post-login redirect
- Allows access to protected routes if authenticated

**Usage in Routes**:

```typescript
{
  path: 'workspaces',
  loadChildren: () => import('./features/workspace/workspace.module'),
  canActivate: [authGuard]  // Protect this route
}
```

### 5. AuthInterceptor

**Location**: `src/app/core/interceptors/auth.interceptor.ts`

**Implementation**: Functional interceptor using `HttpInterceptorFn`

**Features**:

- Automatically adds `Authorization: Bearer <token>` header to all requests
- Handles **401 Unauthorized** errors:
  - Logs out user
  - Redirects to login with session expired message
- Handles **403 Forbidden** errors:
  - Logs error to console
  - Passes error through for component-level handling
- Already configured in `app.config.ts`

**Behavior**:

```typescript
// Automatic header injection
GET /api/workspaces
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

// 401 Error handling
Response: 401 Unauthorized
→ Logs out user
→ Navigates to /auth/login?message=Session expired
→ Shows toast notification

// 403 Error handling
Response: 403 Forbidden
→ Logs to console
→ Error passed to component
→ Component can show appropriate message
```

## Models

**Location**: `src/app/core/models/auth.models.ts`

```typescript
export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: User;
}

export interface User {
  id: string;
  username: string;
  email: string;
}

export interface RegisterDTO {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}
```

## Routing Configuration

**Main Routes** (`app.routes.ts`):

```typescript
{
  path: '',
  redirectTo: '/auth/login',
  pathMatch: 'full',
},
{
  path: 'auth',
  loadChildren: () => import('./features/auth/auth.module')
},
{
  path: 'workspaces',
  loadChildren: () => import('./features/workspace/workspace.module'),
  canActivate: [authGuard]  // Protected route
}
```

**Auth Module Routes** (`auth-routing.module.ts`):

```typescript
{
  path: 'login',
  loadComponent: () => import('./login/login.component')
},
{
  path: 'register',
  loadComponent: () => import('./register/register.component')
}
```

## Styling

### PrimeNG Components Used

- `p-card`: Card container for forms
- `p-inputText`: Text input fields
- `p-password`: Password input with toggle mask and strength meter
- `p-button`: Styled buttons with loading states
- `p-toast`: Toast notifications for messages

### Bootstrap Classes Used

- Responsive grid: `container-fluid`, `row`, `col-*`
- Spacing utilities: `mb-3`, `mb-4`, `mt-1`, etc.
- Text utilities: `text-center`, `text-muted`, `text-danger`
- Form utilities: `form-label`, `fw-semibold`

### Custom Styling

- Gradient backgrounds for auth pages
- Card shadows and border radius
- Smooth transitions and hover effects
- Responsive breakpoints for mobile/tablet/desktop
- Color scheme matching PrimeNG theme

## Environment Configuration

**Development** (`src/environments/environment.ts`):

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000',
};
```

**Production** (`src/environments/environment.prod.ts`):

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.your-domain.com',
};
```

## API Integration

The authentication system expects the following API endpoints:

### POST /api/auth/login

**Request**:

```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### POST /api/auth/register

**Request**:

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):

```json
{}
```

### GET /api/auth/me

**Headers**:

```
Authorization: Bearer <token>
```

**Response** (200 OK):

```json
{
  "id": "uuid-here",
  "username": "johndoe",
  "email": "john@example.com"
}
```

## Testing

### Manual Testing Checklist

**Login Component**:

- [ ] Empty form shows validation errors on submit
- [ ] Invalid credentials show error toast
- [ ] Successful login navigates to /workspaces
- [ ] Token is stored in localStorage
- [ ] Loading spinner shows during API call

**Register Component**:

- [ ] All validation rules work correctly
- [ ] Password strength meter updates in real-time
- [ ] Passwords must match
- [ ] Success shows toast and redirects to login
- [ ] Server errors are displayed

**Auth Guard**:

- [ ] Unauthenticated users redirected to login
- [ ] Authenticated users can access protected routes
- [ ] Return URL is preserved

**Auth Interceptor**:

- [ ] Token is added to all API requests
- [ ] 401 errors log out user
- [ ] 403 errors are logged

## Security Considerations

1. **Token Storage**: JWT tokens stored in localStorage (consider httpOnly cookies for production)
2. **Token Expiration**: Checked on every `isAuthenticated()` call
3. **HTTPS**: Always use HTTPS in production
4. **Password Requirements**: Strong password policy enforced
5. **XSS Protection**: Angular's built-in sanitization
6. **CSRF Protection**: Consider adding CSRF tokens for state-changing operations

## Troubleshooting

### "Session expired" message on every page load

- Check if backend JWT expiration time is correct
- Verify token is being stored in localStorage
- Check token validation logic in `isAuthenticated()`

### Login successful but user not redirected

- Check if `/workspaces` route exists
- Verify authGuard is not preventing navigation
- Check browser console for routing errors

### API calls not including token

- Verify authInterceptor is registered in `app.config.ts`
- Check if token exists in localStorage
- Verify `getToken()` returns the token correctly

### Password validation not working

- Check custom validators are correctly implemented
- Verify form validators are added to FormGroup
- Check if errors are properly displayed in template

## Future Enhancements

- [ ] Implement refresh token rotation
- [ ] Add "Remember Me" functionality
- [ ] Implement "Forgot Password" flow
- [ ] Add social authentication (Google, GitHub)
- [ ] Implement 2FA/MFA
- [ ] Add account verification via email
- [ ] Implement rate limiting for failed login attempts
- [ ] Add session timeout warning

## Dependencies

```json
{
  "@angular/animations": "^20.2.0",
  "@angular/common": "^20.2.0",
  "@angular/forms": "^20.2.0",
  "@angular/router": "^20.2.0",
  "primeng": "^20.3.0",
  "primeicons": "^7.0.0",
  "bootstrap": "^5.3.8",
  "rxjs": "~7.8.0"
}
```

## Support

For issues or questions:

- Check Angular console for errors
- Verify API endpoints are accessible
- Check network tab for request/response details
- Review component and service code

---

**Created**: November 2025  
**Last Updated**: November 2025  
**Version**: 1.0.0
