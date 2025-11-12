# Quick Start - Authentication System

## 🚀 Getting Started

### Prerequisites

- Node.js and npm installed
- Angular CLI installed (`npm install -g @angular/cli`)
- Backend API running on http://localhost:5000

### Installation

1. **Install dependencies** (if not already done):

   ```bash
   cd rag-chatbot-frontend
   npm install
   ```

2. **Start the development server**:

   ```bash
   npm start
   # or
   ng serve
   ```

3. **Open your browser**:
   ```
   http://localhost:4200
   ```

## 📋 Test the Implementation

### 1. Register a New User

Navigate to: http://localhost:4200/auth/register

**Test Data**:

```
Username: testuser
Email: test@example.com
Password: Test123!@#
Confirm Password: Test123!@#
```

**Expected Behavior**:

- ✅ Password strength meter shows "Strong"
- ✅ All validation passes
- ✅ Success toast notification appears
- ✅ Automatically redirects to login after 2 seconds

### 2. Login

Navigate to: http://localhost:4200/auth/login

**Test Data**:

```
Username: testuser
Password: Test123!@#
```

**Expected Behavior**:

- ✅ Success toast notification
- ✅ Redirects to /workspaces
- ✅ Token stored in localStorage

**Verify Token Storage**:
Open DevTools → Application → Local Storage → http://localhost:4200

- Should see: `access_token` with JWT value
- Should see: `refresh_token` with JWT value

### 3. Test Protected Routes

Try accessing: http://localhost:4200/workspaces

**When Logged In**:

- ✅ Page loads normally

**When Logged Out**:

- ✅ Redirects to /auth/login
- ✅ Return URL preserved in query params

### 4. Test Logout

From any protected page, logout using the profile menu or by calling:

```typescript
this.authService.logout();
```

**Expected Behavior**:

- ✅ Tokens removed from localStorage
- ✅ Redirects to /auth/login
- ✅ Cannot access protected routes

### 5. Test Session Expiration

1. Manually modify the token in localStorage to an expired one
2. Try to access a protected route
3. **Expected**: Redirected to login with "Session expired" message

## 🔍 Verify Each Feature

### Login Component Features

- [ ] Empty form shows validation errors
- [ ] Wrong credentials show error toast
- [ ] Correct credentials login successfully
- [ ] Loading spinner appears during API call
- [ ] Successful login navigates to workspaces
- [ ] Responsive on mobile devices

### Register Component Features

- [ ] Username must be at least 3 characters
- [ ] Email must be valid format
- [ ] Password must be at least 8 characters
- [ ] Password must contain uppercase, lowercase, number, special char
- [ ] Password strength meter updates in real-time
- [ ] Confirm password must match
- [ ] Success shows toast and redirects
- [ ] Responsive on mobile devices

### Security Features

- [ ] Auth guard blocks unauthenticated access
- [ ] Token automatically added to API requests
- [ ] 401 errors log out user
- [ ] Token expiration is validated
- [ ] Logout clears all tokens

## 🎯 Component Integration Examples

### Using AuthService in Your Components

```typescript
import { Component, OnInit } from '@angular/core';
import { AuthService } from './core/services/auth.service';

export class MyComponent implements OnInit {
  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Check if user is authenticated
    if (this.authService.isAuthenticated()) {
      console.log('User is logged in');
    }

    // Subscribe to current user
    this.authService.currentUser$.subscribe((user) => {
      if (user) {
        console.log('Current user:', user.username);
      }
    });
  }

  logout() {
    this.authService.logout();
  }
}
```

### Protecting Routes

```typescript
// In your routing module
{
  path: 'protected',
  component: ProtectedComponent,
  canActivate: [authGuard]  // Add this line
}
```

### Making Authenticated API Calls

```typescript
// Token is automatically added by AuthInterceptor
this.http.get('/api/workspaces').subscribe({
  next: (data) => console.log(data),
  error: (error) => {
    if (error.status === 401) {
      // User will be automatically logged out
    }
  },
});
```

## 🐛 Troubleshooting

### Issue: "Cannot find module" errors

**Solution**: Run `npm install` to ensure all dependencies are installed

### Issue: Login succeeds but user not redirected

**Solution**:

- Check if /workspaces route exists
- Verify router is properly configured
- Check browser console for errors

### Issue: Token not added to requests

**Solution**:

- Verify authInterceptor is registered in app.config.ts
- Check localStorage has the token
- Ensure you're using HttpClient (not HttpBackend)

### Issue: Password validation not working

**Solution**:

- Clear browser cache
- Check FormControl validators are set correctly
- Verify custom validators are implemented

### Issue: PrimeNG components not styled

**Solution**:

- Check angular.json includes PrimeNG CSS
- Verify primeicons CSS is loaded
- Check browser DevTools for CSS loading errors

## 📱 Mobile Testing

Test on different screen sizes:

- 📱 Mobile: < 576px
- 📱 Tablet: 576px - 992px
- 💻 Desktop: > 992px

**Chrome DevTools**:

1. Press F12
2. Click device toolbar icon (or Ctrl+Shift+M)
3. Select device or set custom dimensions

## 🔗 Useful Commands

```bash
# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test

# Lint code
ng lint

# Format code (if Prettier is configured)
npx prettier --write "src/**/*.{ts,html,scss}"
```

## 📚 Resources

- **Component Documentation**: See `AUTH_COMPONENTS_GUIDE.md`
- **Implementation Details**: See `AUTH_IMPLEMENTATION_SUMMARY.md`
- **PrimeNG Docs**: https://primeng.org/
- **Angular Docs**: https://angular.dev/
- **Bootstrap Docs**: https://getbootstrap.com/

## ✅ Checklist Before Going to Production

- [ ] Update environment.prod.ts with production API URL
- [ ] Enable HTTPS
- [ ] Implement refresh token rotation
- [ ] Add rate limiting for login attempts
- [ ] Set up proper CORS configuration
- [ ] Consider httpOnly cookies instead of localStorage
- [ ] Add logging and monitoring
- [ ] Test on multiple browsers
- [ ] Test on multiple devices
- [ ] Add error tracking (e.g., Sentry)

## 🎉 Success Indicators

You've successfully implemented authentication if:

- ✅ Users can register with validation
- ✅ Users can login and receive JWT token
- ✅ Token is automatically added to API requests
- ✅ Protected routes redirect unauthenticated users
- ✅ Users can logout and tokens are cleared
- ✅ UI is responsive and looks good on all devices
- ✅ Error messages are clear and helpful
- ✅ Loading states provide feedback

---

**Happy Coding! 🚀**

For questions or issues, refer to the comprehensive guide in `AUTH_COMPONENTS_GUIDE.md`
