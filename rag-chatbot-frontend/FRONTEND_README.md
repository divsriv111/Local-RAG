# RAG Chatbot Frontend

Angular 20 application with PrimeNG and Bootstrap for the RAG-based PDF Chatbot.

## Project Structure

```
src/
├── app/
│   ├── core/                    # Core module (singleton services, guards, interceptors)
│   │   ├── services/
│   │   │   └── auth.service.ts  # Authentication service
│   │   ├── guards/
│   │   │   └── auth.guard.ts    # Route guard for protected routes
│   │   ├── interceptors/
│   │   │   └── auth.interceptor.ts  # HTTP interceptor for JWT
│   │   └── core.module.ts
│   │
│   ├── shared/                  # Shared module (reusable components, pipes, directives)
│   │   ├── components/
│   │   ├── pipes/
│   │   ├── directives/
│   │   └── shared.module.ts
│   │
│   ├── features/                # Feature modules
│   │   ├── auth/               # Authentication module
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── profile/
│   │   │   ├── auth.module.ts
│   │   │   └── auth-routing.module.ts
│   │   ├── workspace/          # Workspace management module
│   │   │   └── workspace.module.ts
│   │   └── chat/               # Chat interface module
│   │       └── chat.module.ts
│   │
│   ├── app.ts                  # Main app component
│   ├── app.html                # App template
│   ├── app.config.ts           # App configuration
│   └── app.routes.ts           # App routing
│
├── environments/
│   ├── environment.ts          # Development environment
│   └── environment.prod.ts     # Production environment
│
└── styles.scss                 # Global styles

```

## Technology Stack

- **Angular**: v20 (zoneless)
- **PrimeNG**: UI component library
- **Bootstrap**: v5 for responsive grid system
- **RxJS**: Reactive programming
- **TypeScript**: Type-safe development

## Available Scripts

### Development Server
```bash
npm start
# or
ng serve
```
Navigate to `http://localhost:4200/`

### Build
```bash
npm run build
# or
ng build
```
Build artifacts will be stored in the `dist/` directory.

### Production Build
```bash
npm run build -- --configuration production
```

### Run Tests
```bash
npm test
# or
ng test
```

### Code Linting
```bash
ng lint
```

## Features Implemented

### Core Module
- ✅ Authentication Service with JWT
- ✅ Auth Guard for route protection
- ✅ HTTP Interceptor for adding Authorization headers
- ✅ Error handling and token expiration checks

### Auth Module
- ✅ Login Component
- ✅ Register Component
- ✅ Profile Component (stub)
- ✅ Lazy-loaded routing

### Shared Module
- ✅ Common imports (Forms, ReactiveFormsModule)
- ✅ Ready for shared components, pipes, and directives

### Workspace & Chat Modules
- ✅ Module structure created
- ⏳ Components to be implemented

## Configuration

### Environment Variables

**Development** (`src/environments/environment.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000'
};
```

**Production** (`src/environments/environment.prod.ts`):
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api-url.com'
};
```

### Styling

The application uses:
- **PrimeNG Theme**: Lara Light Blue
- **Bootstrap 5**: For responsive grid
- **Custom SCSS**: Global styles in `styles.scss`

All CSS dependencies are configured in `angular.json`:
- PrimeNG theme
- PrimeNG core styles
- PrimeIcons
- Bootstrap

## Routing

The application uses lazy loading for all feature modules:

- `/` → Redirects to `/auth/login`
- `/auth/login` → Login page
- `/auth/register` → Registration page
- `/auth/profile` → User profile (protected)
- `/workspaces` → Workspace list (protected)
- `/chat` → Chat interface (protected)

Protected routes require authentication via `authGuard`.

## Next Steps

### To Implement:
1. **Workspace Module**
   - Workspace list component
   - Workspace detail component
   - Create workspace dialog
   - Workspace service

2. **Chat Module**
   - Chat interface component
   - Message display component
   - PDF upload component
   - Chat history sidebar

3. **Shared Components**
   - Loading spinner
   - Error message component
   - Confirmation dialog

4. **Additional Services**
   - Workspace service
   - Chat service
   - PDF service
   - LLM service

## Dependencies

```json
{
  "dependencies": {
    "@angular/animations": "^20.x",
    "@angular/common": "^20.x",
    "@angular/compiler": "^20.x",
    "@angular/core": "^20.x",
    "@angular/forms": "^20.x",
    "@angular/platform-browser": "^20.x",
    "@angular/router": "^20.x",
    "bootstrap": "^5.x",
    "primeng": "^18.x",
    "primeicons": "^7.x",
    "rxjs": "^7.x",
    "tslib": "^2.x",
    "zone.js": "^0.15.x"
  }
}
```

## Notes

- This is an Angular v20 application using **zoneless** change detection
- Uses **standalone components** for auth features
- Uses **traditional modules** for feature organization
- Follows **Clean Architecture** principles
- Ready for integration with ASP.NET Core backend

## License

MIT
