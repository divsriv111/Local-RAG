# Chat History Sidebar - Quick Reference Card

## 📦 Installation (One Command)

```bash
npm install primeng primeicons bootstrap
```

## 🚀 Basic Usage

```typescript
<app-chat-history-sidebar
  [workspaceId]="workspaceId"
  [activeChatId]="activeChatId"
  (chatSelected)="onChatSelected($event)"
  (newChatCreated)="onNewChatCreated($event)"
></app-chat-history-sidebar>
```

## 📂 Files Location

```
src/app/
├── core/
│   ├── models/chat-history.model.ts
│   └── services/chat-history.service.ts
├── features/chat/
│   ├── chat-history-sidebar.component.ts
│   ├── chat-history-sidebar.component.html
│   └── chat-history-sidebar.component.scss
└── shared/pipes/
    └── relative-time.pipe.ts
```

## 🎯 Component Inputs/Outputs

```typescript
// Inputs
@Input() workspaceId: string;           // Required
@Input() activeChatId: string | null;   // Optional

// Outputs
@Output() chatSelected = EventEmitter<ChatHistory>();
@Output() newChatCreated = EventEmitter<ChatHistory>();
```

## 🔌 Required API Endpoints

```
GET    /api/workspaces/{id}/chats?includeArchived=false
POST   /api/workspaces/{id}/chats
PUT    /api/chats/{id}/archive
DELETE /api/chats/{id}
```

## 🎨 Features Checklist

- [x] List chat histories
- [x] Relative timestamps (5 mins ago, 2 hours ago)
- [x] Active chat highlighting
- [x] New chat button
- [x] Context menu (Archive, Delete)
- [x] Delete confirmation dialog
- [x] Archive filter toggle
- [x] Message count badge
- [x] Responsive mobile view
- [x] Loading states
- [x] Empty states
- [x] Error handling with toasts

## 📱 Responsive Breakpoints

- Desktop: `> 768px` - Fixed sidebar
- Mobile: `≤ 768px` - Hamburger + overlay

## ⚙️ Environment Setup

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000',
};
```

## 🎨 Theme Configuration (angular.json)

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css",
  "node_modules/bootstrap/dist/css/bootstrap.min.css",
  "src/styles.scss"
]
```

## 🔍 Service Methods Quick Reference

```typescript
// ChatHistoryService
getAll(workspaceId: string, includeArchived: boolean): Observable<ChatHistory[]>
create(workspaceId: string): Observable<ChatHistory>
archive(chatId: string): Observable<void>
delete(chatId: string): Observable<void>
getById(chatId: string): Observable<ChatHistory>
```

## 🎭 ChatHistory Interface

```typescript
interface ChatHistory {
  id: string;
  workspaceId: string;
  name: string;
  firstQuery: string;
  createdAt: Date;
  isArchived: boolean;
  messageCount?: number;
  updatedAt?: Date;
}
```

## 🛠️ Customization Examples

### Change Archive Toggle Color

```scss
.toggle-switch input:checked + .toggle-label {
  background-color: #10b981; // Green instead of primary
}
```

### Adjust Sidebar Width

```scss
.sidebar-left {
  width: 25%; // Desktop
  min-width: 300px; // Minimum
  max-width: 400px; // Maximum
}
```

### Change Mobile Breakpoint

```scss
@media (max-width: 992px) {
  // Was 768px
  .chat-history-sidebar {
    display: none;
  }
}
```

## 🐛 Common Issues & Fixes

### Issue: Styles not loading

```bash
# Restart dev server after angular.json changes
npm start
```

### Issue: API calls failing

```typescript
// Check environment.ts
console.log(environment.apiUrl);

// Verify CORS on backend
// Add Authorization header in interceptor
```

### Issue: Module not found

```bash
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation Files

- `CHAT_HISTORY_SIDEBAR_SUMMARY.md` - Complete overview
- `CHAT_HISTORY_SIDEBAR_README.md` - Usage guide
- `CHAT_HISTORY_SIDEBAR_INSTALLATION.md` - Setup guide
- `workspace-detail.component.example.*` - Integration example

## ⚡ Performance Tips

```typescript
// Enable OnPush for better performance
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})

// Use trackBy for ngFor
trackByChatId(index: number, chat: ChatHistory): string {
  return chat.id;
}
```

## 🔐 Security Checklist

- [x] JWT authentication via HTTP interceptor
- [x] CORS configured on backend
- [x] Input validation on all forms
- [x] XSS protection (Angular sanitization)
- [x] CSRF tokens (if needed)

## 📞 Support

- Check browser console for errors
- Verify API responses in Network tab
- Review documentation files
- Test API endpoints with Postman/curl

## ✅ Status

**Ready for Production** ✨

---

**Created**: November 2025  
**Angular Version**: 18+  
**PrimeNG Version**: 17+  
**License**: MIT
