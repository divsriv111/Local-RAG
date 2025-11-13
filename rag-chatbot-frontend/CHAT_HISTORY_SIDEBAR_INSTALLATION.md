# Chat History Sidebar Component - Installation & Setup Guide

## Quick Installation

Run the following commands to install all required dependencies:

```bash
cd rag-chatbot-frontend

# Install PrimeNG and PrimeIcons
npm install primeng primeicons

# Install Bootstrap (if not already installed)
npm install bootstrap
```

## Configure angular.json

Add the required CSS files to your `angular.json` in the `styles` array:

```json
{
  "projects": {
    "rag-chatbot-frontend": {
      "architect": {
        "build": {
          "options": {
            "styles": [
              "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
              "node_modules/primeng/resources/primeng.min.css",
              "node_modules/primeicons/primeicons.css",
              "node_modules/bootstrap/dist/css/bootstrap.min.css",
              "src/styles.scss"
            ]
          }
        }
      }
    }
  }
}
```

## Component Files Structure

The component has been created with the following files:

```
rag-chatbot-frontend/src/app/
├── core/
│   ├── models/
│   │   └── chat-history.model.ts          # TypeScript interfaces
│   └── services/
│       └── chat-history.service.ts        # HTTP service for API calls
├── features/
│   └── chat/
│       ├── chat-history-sidebar.component.ts     # Component logic
│       ├── chat-history-sidebar.component.html   # Template
│       └── chat-history-sidebar.component.scss   # Styles
└── shared/
    └── pipes/
        └── relative-time.pipe.ts          # Time formatting pipe
```

## Usage in Your Application

### 1. Import the Component

Since this is a standalone component, simply import it where needed:

```typescript
import { Component } from '@angular/core';
import { ChatHistorySidebarComponent } from './features/chat/chat-history-sidebar.component';

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [ChatHistorySidebarComponent],
  template: `
    <div class="workspace-container">
      <app-chat-history-sidebar
        [workspaceId]="workspaceId"
        [activeChatId]="activeChatId"
        (chatSelected)="onChatSelected($event)"
        (newChatCreated)="onNewChatCreated($event)"
      ></app-chat-history-sidebar>
    </div>
  `,
})
export class WorkspaceComponent {
  workspaceId = 'your-workspace-id';
  activeChatId: string | null = null;

  onChatSelected(chat: any) {
    this.activeChatId = chat.id;
    // Load messages for the selected chat
  }

  onNewChatCreated(chat: any) {
    this.activeChatId = chat.id;
    // Initialize the new chat
  }
}
```

### 2. Configure Environment

Ensure your `environment.ts` file has the correct API URL:

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000',
};

// src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com',
};
```

### 3. Add HTTP Interceptor (Optional but Recommended)

Create an HTTP interceptor to add authentication headers:

```typescript
// src/app/core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('authToken');

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(req);
};
```

Register it in your `app.config.ts`:

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [provideHttpClient(withInterceptors([authInterceptor]))],
};
```

## Backend API Requirements

The component expects these API endpoints to be available:

### 1. Get All Chat Histories

```
GET /api/workspaces/{workspaceId}/chats?includeArchived={boolean}

Response: ChatHistory[]
[
  {
    "id": "guid",
    "workspaceId": "guid",
    "name": "string",
    "firstQuery": "string",
    "createdAt": "ISO 8601 datetime",
    "isArchived": boolean,
    "messageCount": number (optional),
    "updatedAt": "ISO 8601 datetime" (optional)
  }
]
```

### 2. Create New Chat

```
POST /api/workspaces/{workspaceId}/chats

Request Body:
{
  "workspaceId": "guid"
}

Response: ChatHistory
{
  "id": "guid",
  "workspaceId": "guid",
  "name": "New Chat",
  "firstQuery": "",
  "createdAt": "ISO 8601 datetime",
  "isArchived": false
}
```

### 3. Archive Chat

```
PUT /api/chats/{chatId}/archive

Response: 200 OK
```

### 4. Delete Chat

```
DELETE /api/chats/{chatId}

Response: 204 No Content
```

## Testing the Component

### 1. Run the Development Server

```bash
npm start
# or
ng serve
```

### 2. Navigate to the Component

Open your browser to `http://localhost:4200` and navigate to the workspace page.

### 3. Test Functionality

- Click "New Chat" to create a chat
- Click on a chat to select it
- Right-click or use the kebab menu to archive/delete
- Toggle "Show Archived" to filter

## Troubleshooting

### Issue: PrimeNG styles not loading

**Solution**: Verify `angular.json` includes all PrimeNG CSS files. Restart the dev server after making changes.

### Issue: API calls failing

**Solution**:

1. Check the API URL in `environment.ts`
2. Verify CORS is enabled on the backend
3. Check browser console for detailed errors
4. Ensure authentication token is being sent

### Issue: Relative time not updating

**Solution**: The pipe is pure and only updates when the input reference changes. For real-time updates, consider using an impure pipe or implementing a timer.

### Issue: Module not found errors

**Solution**: Ensure all dependencies are installed:

```bash
npm install
```

If issues persist, delete `node_modules` and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Customization

### Change Theme

PrimeNG supports multiple themes. Change the theme in `angular.json`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-dark-blue/theme.css",
  // ... other styles
]
```

Available themes:

- `lara-light-blue`
- `lara-dark-blue`
- `lara-light-indigo`
- `lara-dark-indigo`
- And many more...

### Customize Colors

Override CSS variables in your `styles.scss`:

```scss
:root {
  --primary-color: #3b82f6;
  --primary-50: #eff6ff;
  --surface-0: #ffffff;
  --surface-50: #f9fafb;
  --text-color: #1f2937;
  --text-color-secondary: #6b7280;
}
```

### Adjust Mobile Breakpoint

Modify the breakpoint in the SCSS file:

```scss
@media (max-width: 992px) {
  // Changed from 768px
  .chat-history-sidebar {
    display: none;
  }
}
```

## Performance Optimization

### Enable OnPush Change Detection

For better performance with large chat lists:

```typescript
@Component({
  // ...
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatHistorySidebarComponent {
  // Inject ChangeDetectorRef
  constructor(private cdr: ChangeDetectorRef) // ... other dependencies
  {}

  // Manually trigger change detection when needed
  loadChatHistories(): void {
    // ... load data
    this.cdr.markForCheck();
  }
}
```

### Virtual Scrolling for Large Lists

For workspaces with hundreds of chats, consider implementing virtual scrolling using Angular CDK.

## Next Steps

1. Integrate with your chat interface component
2. Connect to your PDF upload component
3. Implement message loading when chat is selected
4. Add additional features like search and sorting
5. Implement chat rename functionality (currently disabled)

## Support

For issues or questions:

- Check the README: `CHAT_HISTORY_SIDEBAR_README.md`
- Review component documentation
- Check API endpoint responses in browser DevTools

## Version Compatibility

- Angular: 18+
- PrimeNG: 17+
- Bootstrap: 5+
- TypeScript: 5+
