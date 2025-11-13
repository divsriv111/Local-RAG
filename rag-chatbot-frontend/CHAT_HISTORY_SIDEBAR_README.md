# Chat History Sidebar Component

## Overview

The ChatHistorySidebarComponent provides a comprehensive interface for managing and navigating chat histories within a workspace. It includes features like creating new chats, archiving, deleting, and filtering chat histories.

## Features

### Core Functionality

- ✅ Display list of chat histories for the current workspace
- ✅ Show chat name (auto-generated from first query)
- ✅ Show relative timestamps ("5 mins ago", "2 hours ago", "3 days ago")
- ✅ Highlight active/selected chat
- ✅ "New Chat" button for creating new conversations
- ✅ Context menu with Archive and Delete options
- ✅ Delete confirmation dialog
- ✅ Filter to show/hide archived chats
- ✅ Message count display (optional)

### Visual Design

- Scrollable list with fixed height and overflow-y: auto
- Hover effects on chat items
- Active chat with distinct background color
- PrimeNG Menu for context actions
- Loading states and empty states
- Smooth animations

### Responsive Behavior

- Desktop: Fixed sidebar visible at all times
- Mobile: Collapsible sidebar with hamburger menu
- Mobile: Overlay sidebar using PrimeNG Sidebar component

## Files Created

1. **Component Files**

   - `chat-history-sidebar.component.ts` - Component logic
   - `chat-history-sidebar.component.html` - Template
   - `chat-history-sidebar.component.scss` - Styles

2. **Service**

   - `chat-history.service.ts` - API integration service

3. **Models**

   - `chat-history.model.ts` - TypeScript interfaces

4. **Pipes**
   - `relative-time.pipe.ts` - Formats timestamps as relative time

## Usage Example

```typescript
import { Component } from '@angular/core';
import { ChatHistorySidebarComponent } from './features/chat/chat-history-sidebar.component';
import { ChatHistory } from './core/models/chat-history.model';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [ChatHistorySidebarComponent],
  template: `
    <div class="workspace-layout">
      <!-- Left Sidebar: Chat History -->
      <div class="sidebar-left">
        <app-chat-history-sidebar
          [workspaceId]="workspaceId"
          [activeChatId]="activeChatId"
          (chatSelected)="onChatSelected($event)"
          (newChatCreated)="onNewChatCreated($event)"
        ></app-chat-history-sidebar>
      </div>

      <!-- Center Panel: Chat Interface -->
      <div class="main-content">
        <!-- Your chat interface component here -->
      </div>

      <!-- Right Sidebar: PDF Upload -->
      <div class="sidebar-right">
        <!-- Your PDF upload component here -->
      </div>
    </div>
  `,
  styles: [
    `
      .workspace-layout {
        display: flex;
        height: 100vh;
      }

      .sidebar-left {
        width: 20%;
        min-width: 280px;
        max-width: 320px;
      }

      .main-content {
        flex: 1;
      }

      .sidebar-right {
        width: 20%;
        min-width: 280px;
        max-width: 320px;
      }

      @media (max-width: 768px) {
        .workspace-layout {
          flex-direction: column;
        }

        .sidebar-left,
        .sidebar-right {
          width: 100%;
          max-width: 100%;
        }
      }
    `,
  ],
})
export class WorkspaceDetailComponent {
  workspaceId = 'your-workspace-id';
  activeChatId: string | null = null;

  onChatSelected(chat: ChatHistory): void {
    this.activeChatId = chat.id;
    console.log('Selected chat:', chat);
    // Load messages for this chat
  }

  onNewChatCreated(chat: ChatHistory): void {
    this.activeChatId = chat.id;
    console.log('New chat created:', chat);
    // Switch to the new chat
  }
}
```

## Component API

### Inputs

- `workspaceId: string` (required) - The ID of the current workspace
- `activeChatId: string | null` - The ID of the currently active chat

### Outputs

- `chatSelected: EventEmitter<ChatHistory>` - Emitted when a chat is selected
- `newChatCreated: EventEmitter<ChatHistory>` - Emitted when a new chat is created

## Service Methods

### ChatHistoryService

```typescript
// Get all chat histories for a workspace
getAll(workspaceId: string, includeArchived: boolean = false): Observable<ChatHistory[]>

// Create a new chat history
create(workspaceId: string): Observable<ChatHistory>

// Archive a chat history
archive(chatId: string): Observable<void>

// Delete a chat history
delete(chatId: string): Observable<void>

// Get a single chat history by ID
getById(chatId: string): Observable<ChatHistory>
```

## PrimeNG Dependencies

Make sure to install the required PrimeNG modules:

```bash
npm install primeng primeicons
```

Required PrimeNG modules:

- `ButtonModule`
- `SidebarModule`
- `MenuModule`
- `ConfirmDialogModule`
- `ToastModule`
- `InputSwitchModule`

## Environment Configuration

Ensure your `environment.ts` file has the API URL configured:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000',
};
```

## Backend API Endpoints

The component expects the following API endpoints:

```
GET    /api/workspaces/{workspaceId}/chats?includeArchived={bool}
POST   /api/workspaces/{workspaceId}/chats
GET    /api/chats/{chatId}
PUT    /api/chats/{chatId}/archive
DELETE /api/chats/{chatId}
```

## Styling

The component uses CSS custom properties (CSS variables) for theming. Ensure your theme defines:

- `--surface-0`, `--surface-50`, `--surface-100`, etc.
- `--primary-color`, `--primary-50`
- `--text-color`, `--text-color-secondary`
- `--surface-border`
- `--red-600`, `--red-50` (for delete actions)
- `--orange-600`, `--orange-50` (for archived badge)

## Responsive Breakpoints

- **Desktop**: `> 768px` - Full sidebar visible
- **Mobile**: `≤ 768px` - Hamburger menu with overlay sidebar

## Accessibility

- Keyboard navigation support
- Focus indicators on chat items
- ARIA labels for buttons and menus
- Screen reader friendly

## Future Enhancements (Currently Disabled)

- **Rename Chat**: Placeholder added but disabled for MVP
- **Chat Search**: Search/filter by chat name
- **Drag & Drop Reordering**: Reorder chat histories
- **Bulk Actions**: Select multiple chats for batch operations

## Troubleshooting

### Module Not Found Errors

If you see errors about missing PrimeNG modules, install them:

```bash
npm install primeng@latest primeicons@latest
```

### API Connection Issues

Verify the `apiUrl` in your environment configuration matches your backend URL.

### Styling Issues

Ensure PrimeNG CSS is imported in `angular.json`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css",
  "src/styles.scss"
]
```

## Notes

- The component is standalone and can be used independently
- All API calls include proper error handling with toast notifications
- The component automatically handles loading states
- Mobile view uses PrimeNG Sidebar for better UX
- Context menu works with both right-click and kebab menu button
