# Application Layout Implementation

This document describes the main application layout with navigation and responsive design.

## Components Implemented

### 1. App Component (`app.component.ts/html/scss`)

The main application component with:

- **Top Navigation Bar** featuring:

  - Logo/app name (clickable, navigates to workspaces)
  - Theme toggle button (light/dark mode)
  - User menu dropdown (Profile, Logout)
  - Fully responsive with hamburger menu for mobile

- **Navigation Structure**:

  - **Public routes**: `/login`, `/register`
  - **Protected routes**: `/workspaces`, `/workspace/:id`, `/profile`
  - **Error routes**: `/error/404`, `/error/403`, `/error/500`
  - Auto-redirect to `/workspaces` after login
  - Auto-redirect to `/login` if not authenticated

- **Responsive Behavior**:
  - **Desktop (>992px)**: Full navigation bar with all items visible
  - **Tablet (768px-992px)**: Compact navigation
  - **Mobile (<768px)**: Hamburger menu with PrimeNG Drawer sidebar

### 2. Error Component (`error.component.ts/html/scss`)

Handles all error scenarios:

- 404 (Page Not Found)
- 401 (Unauthorized)
- 403 (Forbidden)
- 500 (Internal Server Error)
- 503 (Service Unavailable)

Features:

- Dynamic error messages based on error code
- Animated error icons
- "Go Home" and "Go Back" action buttons
- Fully responsive design
- Gradient background with card layout

### 3. Theme Service (`theme.service.ts`)

Manages application theming:

- Light/Dark theme toggle
- Persists theme preference in localStorage
- Detects system theme preference
- Observable theme state for reactive updates
- Smooth transitions between themes

### 4. Global Styles (`styles.scss`)

Enhanced with:

- **CSS Variables** for colors, spacing, shadows, transitions
- **Responsive Breakpoints**: xs, sm, md, lg, xl
- **Utility Classes**:
  - Layout (flex, grid, display)
  - Spacing (margin, padding)
  - Sizing (width, height)
  - Text utilities (alignment, weight, transform)
  - Border utilities (radius, shadows)
  - Position utilities
- **Animation Utilities**: fadeIn, slideInUp, slideInDown, scaleIn
- **Mobile-first responsive design**

## PrimeNG Configuration

### Theme Setup

PrimeNG 20+ themes configured in `angular.json`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css",
  "node_modules/bootstrap/dist/css/bootstrap.min.css",
  "src/styles.scss"
]
```

### Components Used

- **Menubar**: Desktop navigation
- **Button**: Action buttons throughout
- **Drawer**: Mobile sidebar menu
- **Menu**: User dropdown menu
- **Toast**: Global notifications
- **Card**: Error page layout

## Features

### Authentication Integration

- Subscribes to `AuthService.currentUser$` for reactive UI updates
- Shows/hides navigation based on authentication state
- Displays current username in user menu
- Secure logout with confirmation toast

### Theme Switching

- Toggle between light and dark themes
- Animated theme button (rotates on hover)
- Toast notification on theme change
- Persisted across sessions

### Toast Notifications

Used for:

- Success messages (logout, actions completed)
- Info messages (theme changes)
- Warning messages (user warnings)
- Error messages (failed operations)

### Responsive Design

- **Mobile-first approach**
- Collapsible sidebar for mobile
- Stacked layout on smaller screens
- Touch-friendly button sizes
- Optimized font sizes per breakpoint

## Routing Configuration

### Protected Routes

All workspace, chat, and profile routes require authentication via `authGuard`.

### Error Handling

- Catch-all route (`**`) redirects to 404 error page
- Specific error routes for different error types
- Route guards redirect to login for unauthenticated users

## Usage

### Navigation

```typescript
// Navigate programmatically
navigateTo(path: string): void {
  this.router.navigate([path]);
  this.sidebarVisible = false; // Close mobile menu
}
```

### Theme Toggle

```typescript
// Toggle theme
toggleTheme(): void {
  this.themeService.toggleTheme();
  // Show toast notification
}
```

### Logout

```typescript
// Logout user
logout(): void {
  this.authService.logout();
  // Show success toast
  // Navigate to login
}
```

## Styling Notes

### CSS Variables

All colors and spacing use CSS variables for easy theming:

```scss
--primary-color: #667eea;
--surface-ground: #f8f9fa;
--spacing-md: 1rem;
--border-radius: 8px;
```

### Dark Theme

Activated by setting `data-theme="dark"` on document root. All colors automatically adjust via CSS variables.

### Animations

Smooth transitions on all interactive elements:

- Hover effects on buttons and menu items
- Fade in/out animations
- Slide animations for mobile menu
- Scale animations for modals

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design tested on all screen sizes

## Future Enhancements

- [ ] Add breadcrumb navigation
- [ ] Implement progressive web app (PWA) features
- [ ] Add keyboard shortcuts
- [ ] Enhance accessibility (ARIA labels, screen reader support)
- [ ] Add loading states for route transitions
- [ ] Implement skeleton loaders
