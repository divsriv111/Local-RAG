# Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- npm or yarn

## Running the Application

### 1. Navigate to frontend directory

```bash
cd "/Users/divyanshusrivastava/Local RAG/rag-chatbot-frontend"
```

### 2. Start development server

```bash
npm start
```

### 3. Open browser

Navigate to: **http://localhost:4200**

## Available Routes

- **http://localhost:4200** → Redirects to login
- **http://localhost:4200/auth/login** → Login page
- **http://localhost:4200/auth/register** → Registration page
- **http://localhost:4200/auth/profile** → User profile
- **http://localhost:4200/workspaces** → Workspace list (protected, requires login)
- **http://localhost:4200/chat** → Chat interface (protected, requires login)

## Testing Without Backend

The frontend will work without the backend, but API calls will fail. To test:

1. Visit registration page
2. Try to submit form (will fail with CORS or connection error)
3. This is expected - backend needed for full functionality

## Connecting to Backend

Update `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000', // Your ASP.NET Core API URL
};
```

## Project Structure Overview

```
src/app/
├── core/           # Auth service, guards, interceptors
├── shared/         # Reusable components
└── features/       # Feature modules
    ├── auth/       # Login, register, profile
    ├── workspace/  # Workspace management (to be implemented)
    └── chat/       # Chat interface (to be implemented)
```

## Key Files

- **Auth Service**: `src/app/core/services/auth.service.ts`
- **Auth Guard**: `src/app/core/guards/auth.guard.ts`
- **Login Component**: `src/app/features/auth/login/login.component.ts`
- **Register Component**: `src/app/features/auth/register/register.component.ts`
- **Routes**: `src/app/app.routes.ts`
- **Config**: `src/app/app.config.ts`

## Troubleshooting

### Port already in use

```bash
# Kill process on port 4200
lsof -ti:4200 | xargs kill -9
```

### Node modules issues

```bash
rm -rf node_modules package-lock.json
npm install
```

### Build errors

```bash
npm run build
# Check errors and fix
```

## Next Steps

1. ✅ Frontend setup complete
2. ⏳ Start backend ASP.NET Core API
3. ⏳ Implement workspace components
4. ⏳ Implement chat components
5. ⏳ Add PDF upload functionality

## Documentation

- Full README: `FRONTEND_README.md`
- Setup details: `FRONTEND_SETUP_COMPLETE.md`
