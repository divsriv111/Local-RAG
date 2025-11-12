# Chat Interface - Quick Reference

## 🚀 Quick Start

```typescript
// Import and use in your component
import { ChatInterfaceComponent } from './features/chat/components/chat-interface/chat-interface.component';

// In your template
<app-chat-interface
  [chatId]="'chat-id-123'"
  [workspaceId]="'workspace-id-456'"
  [selectedPdfIds]="['pdf-1', 'pdf-2']"
/>
```

## 📂 File Locations

```
src/app/features/chat/
├── components/
│   ├── chat-interface/
│   │   ├── chat-interface.component.ts      ← Main component
│   │   ├── chat-interface.component.html    ← Template
│   │   └── chat-interface.component.scss    ← Styles
│   └── chat-container/
│       └── chat-container.component.ts      ← Usage example
├── services/
│   └── chat.service.ts                      ← API service
├── models/
│   └── message.model.ts                     ← TypeScript interfaces
├── chat.module.ts                           ← Module config
├── CHAT_INTERFACE_README.md                 ← Full documentation
└── CHAT_INTERFACE_IMPLEMENTATION_SUMMARY.md ← Implementation details
```

## 🎯 Key Features

| Feature             | Status | Description                                          |
| ------------------- | ------ | ---------------------------------------------------- |
| iMessage-style UI   | ✅     | Blue user messages (right), gray bot messages (left) |
| Real-time Streaming | ✅     | Server-Sent Events with token-by-token rendering     |
| Markdown Support    | ✅     | Bold, italic, links, code blocks in bot messages     |
| Source References   | ✅     | Clickable PDF badges with page numbers               |
| LLM Selection       | ✅     | Dropdown: GPT-4 Turbo, GPT-4.1 Mini, Local LLaMA-3   |
| Auto-resize Input   | ✅     | Textarea grows as you type                           |
| Typing Indicator    | ✅     | Animated dots while waiting for response             |
| Character Count     | ✅     | Shows current/max with warning                       |
| Auto-scroll         | ✅     | Scrolls to bottom on new messages                    |
| Mobile Responsive   | ✅     | Works on all screen sizes                            |
| Error Handling      | ✅     | Toast notifications + retry logic                    |
| Loading States      | ✅     | Spinners and animations                              |

## 🔌 Required API Endpoints

### 1. Get Messages

```http
GET /api/chats/{chatId}/messages
Authorization: Bearer {token}

Response: Message[]
```

### 2. Stream LLM Response

```http
POST /api/llm/query
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "Your question",
  "selectedPdfIds": ["pdf-1", "pdf-2"],
  "workspaceId": "workspace-id",
  "chatHistoryId": "chat-id",
  "llmModel": "gpt-4o-mini"
}

Response: text/event-stream
data: {"type":"token","content":"Hello"}
data: {"type":"source","pdf":"doc.pdf","page":5}
data: {"type":"done","answer":"...","references":[...]}
```

### 3. Save Message

```http
POST /api/chats/{chatId}/messages
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "Message text",
  "isUserMessage": false,
  "references": [{"pdf":"doc.pdf","page":5}]
}

Response: Message
```

## 📱 Component Inputs

```typescript
@Input() chatId: string;         // Required - Current chat ID
@Input() workspaceId: string;    // Required - Current workspace ID
@Input() selectedPdfIds: string[]; // Required - Selected PDF IDs
```

## 🎨 Customization Quick Hits

### Change Message Colors

```scss
// chat-interface.component.scss

// User messages
.user-message .message-bubble {
  background: linear-gradient(135deg, #YOUR_COLOR 0%, #DARKER_COLOR 100%);
}

// Bot messages
.bot-message .message-bubble {
  background: #YOUR_BACKGROUND_COLOR;
}
```

### Add/Remove LLM Models

```typescript
// message.model.ts
export const LLM_MODELS: LlmModel[] = [
  { label: 'Your Model', value: 'model-id', description: 'Description' },
];
```

### Change API URL

```typescript
// src/environments/environment.ts
export const environment = {
  apiUrl: 'http://your-api-url/api',
};
```

## ⌨️ Keyboard Shortcuts

| Key             | Action            |
| --------------- | ----------------- |
| **Enter**       | Send message      |
| **Shift+Enter** | New line in input |

## 🐛 Common Issues & Fixes

### Issue: Streaming not working

```typescript
// Fix: Check CORS allows streaming
// Backend: Add header
response.Headers.Add('Content-Type', 'text/event-stream');
```

### Issue: Markdown not rendering

```typescript
// Fix: Ensure MarkdownModule is configured
// app.config.ts
importProvidersFrom(MarkdownModule.forRoot());
```

### Issue: PrimeNG components missing

```bash
# Fix: Install dependencies
npm install primeng@20 @primeng/themes primeicons
```

### Issue: Messages not loading

```typescript
// Fix: Check API URL in environment
console.log(environment.apiUrl);
// Verify authentication token
console.log(localStorage.getItem('token'));
```

## 📊 Performance Tips

1. **TrackBy Function**: Already implemented for ngFor
2. **Debounced Scrolling**: Built-in (100ms delay)
3. **Change Detection**: Manual triggers for streaming
4. **Lazy Loading**: Messages loaded on-demand

## 🔒 Security Checklist

- ✅ JWT tokens in localStorage (consider httpOnly cookies for production)
- ✅ XSS protection via Angular sanitization
- ✅ Input validation on backend
- ⚠️ Add rate limiting on backend
- ⚠️ Use HTTPS in production
- ⚠️ Implement CSRF protection

## 📱 Responsive Breakpoints

```scss
// Desktop: > 992px (full layout)
// Tablet: 768px - 992px (adjusted widths)
// Mobile: < 768px (stacked layout)
```

## 🧪 Testing Checklist

- [ ] Send message with Enter key
- [ ] Send message with Send button
- [ ] New line with Shift+Enter
- [ ] Model selection dropdown works
- [ ] Streaming displays token-by-token
- [ ] Typing indicator appears
- [ ] Source references are clickable
- [ ] Auto-scroll on new messages
- [ ] Character count updates
- [ ] Warning at 90% characters
- [ ] Error toast on failure
- [ ] Retry failed messages
- [ ] Markdown renders correctly
- [ ] Mobile responsive layout
- [ ] Messages load on mount

## 📞 Getting Help

1. Check `CHAT_INTERFACE_README.md` for detailed documentation
2. Review `CHAT_INTERFACE_IMPLEMENTATION_SUMMARY.md`
3. Look at `chat-container.component.ts` for usage example
4. Check browser console for errors
5. Verify API endpoints are responding
6. Test with Postman/curl

## 🎯 Integration Steps

1. **Add to your module/component**

   ```typescript
   import { ChatInterfaceComponent } from './features/chat/components/chat-interface/chat-interface.component';
   ```

2. **Use in template**

   ```html
   <app-chat-interface [chatId]="id" [workspaceId]="wsId" [selectedPdfIds]="pdfs" />
   ```

3. **Provide required inputs**

   - Get chatId from route/state
   - Get workspaceId from route/state
   - Get selectedPdfIds from PDF selector

4. **Configure API endpoints**

   - Update environment.ts
   - Implement backend endpoints
   - Test streaming with curl/Postman

5. **Customize (optional)**
   - Colors in SCSS
   - LLM models in message.model.ts
   - Reference click handler

## ✨ That's It!

Your chat interface is ready to use. Just wire up the inputs and backend API!

---

**Need help?** Check the full README or implementation summary docs.  
**Found a bug?** Check the troubleshooting section first.  
**Want to customize?** See the customization section above.

🚀 **Happy chatting!**
