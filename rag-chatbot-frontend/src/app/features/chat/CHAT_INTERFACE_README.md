# Chat Interface Component

A feature-rich, iMessage-style chat interface component for the RAG chatbot application with real-time streaming, markdown support, and source citations.

## Features

✅ **iMessage-Style UI** - Beautiful message bubbles with user messages on the right (blue) and bot messages on the left (gray)  
✅ **Real-time Streaming** - Connect to ASP.NET API using Server-Sent Events for token-by-token responses  
✅ **Markdown Rendering** - Full markdown support in bot messages (bold, italic, links, code blocks)  
✅ **Source References** - Clickable badges showing PDF sources and page numbers  
✅ **LLM Model Selection** - Dropdown to choose between GPT-4 Turbo, GPT-4.1 Mini, or Local LLaMA-3  
✅ **Auto-resize Input** - Text area automatically expands as you type  
✅ **Typing Indicator** - Animated dots while waiting for LLM response  
✅ **Character Count** - Shows current/max character count with warning  
✅ **Auto-scroll** - Automatically scrolls to bottom on new messages  
✅ **Mobile Responsive** - Fully responsive design for all screen sizes  
✅ **Error Handling** - Comprehensive error handling with retry logic  
✅ **Loading States** - Smooth loading indicators and animations

## Installation

The component has already been created with all necessary files. Dependencies installed:

```bash
npm install ngx-markdown marked
```

## File Structure

```
src/app/features/chat/
├── components/
│   └── chat-interface/
│       ├── chat-interface.component.ts    # Main component logic
│       ├── chat-interface.component.html  # Template
│       └── chat-interface.component.scss  # Styles
├── services/
│   └── chat.service.ts                    # API service with streaming
├── models/
│   └── message.model.ts                   # TypeScript interfaces
└── chat.module.ts                         # Module configuration
```

## Usage

### Basic Usage

```typescript
import { ChatInterfaceComponent } from './features/chat/components/chat-interface/chat-interface.component';

@Component({
  template: `
    <app-chat-interface
      [chatId]="currentChatId"
      [workspaceId]="currentWorkspaceId"
      [selectedPdfIds]="selectedPdfIds"
    />
  `,
})
export class WorkspaceDetailComponent {
  currentChatId = 'chat-id-123';
  currentWorkspaceId = 'workspace-id-456';
  selectedPdfIds = ['pdf-1', 'pdf-2'];
}
```

### Component Inputs

| Input            | Type     | Required | Description                        |
| ---------------- | -------- | -------- | ---------------------------------- |
| `chatId`         | string   | Yes      | The ID of the current chat history |
| `workspaceId`    | string   | Yes      | The ID of the workspace            |
| `selectedPdfIds` | string[] | Yes      | Array of selected PDF document IDs |

## API Integration

### Backend Requirements

The component expects the following API endpoints:

1. **Get Messages**

   - `GET /api/chats/{chatId}/messages`
   - Returns array of messages

2. **Stream LLM Response**

   - `POST /api/llm/query`
   - Accepts: query, workspaceId, chatHistoryId, selectedPdfIds, llmModel
   - Returns: Server-Sent Events stream

3. **Create Message**
   - `POST /api/chats/{chatId}/messages`
   - Saves message to database

### Streaming Response Format

The backend should send Server-Sent Events in this format:

```javascript
// Token chunk
data: {"type":"token","content":"word"}

// Source reference
data: {"type":"source","pdf":"document.pdf","page":5,"pdfId":"pdf-123"}

// Final response
data: {"type":"done","answer":"Complete answer...","references":[...]}

// Error
data: {"type":"error","message":"Error description"}
```

## Customization

### Styling

The component uses CSS variables and can be customized via SCSS:

```scss
// Override message bubble colors
.user-message .message-bubble {
  background: linear-gradient(135deg, #your-color 0%, #your-dark-color 100%);
}

.bot-message .message-bubble {
  background: #your-background-color;
}
```

### LLM Models

Modify available models in `message.model.ts`:

```typescript
export const LLM_MODELS: LlmModel[] = [
  {
    label: 'Your Custom Model',
    value: 'custom-model-id',
    description: 'Model description',
  },
  // ...more models
];
```

## Features in Detail

### 1. Real-time Streaming

The component uses `fetch` API with ReadableStream to handle streaming responses:

```typescript
sendMessageWithFetch(request: SendMessageRequest): Observable<StreamingChunk> {
  // Fetches stream and parses Server-Sent Events
  // Yields chunks as they arrive
}
```

### 2. Markdown Rendering

Uses `ngx-markdown` library with syntax highlighting support:

```html
<markdown [data]="message.content" [inline]="false"></markdown>
```

### 3. Source References

Bot messages can include clickable source references:

```typescript
interface MessageReference {
  pdf: string; // PDF filename
  page: number; // Page number
  pdfId?: string; // PDF document ID
}
```

### 4. Auto-scroll Behavior

Messages container auto-scrolls to bottom using:

- `ViewChild` to access scroll container
- `AfterViewChecked` lifecycle hook
- Debounced scroll subject to optimize performance

### 5. Message Input

- Auto-resizing textarea using PrimeNG
- Enter to send, Shift+Enter for new line
- Character count with warning at 90%
- Disabled when no PDFs selected or while streaming

### 6. Error Handling

- Network errors show toast notification
- Failed messages can be retried
- Graceful degradation on streaming failures

## Responsive Design

The component is fully responsive with breakpoints at:

- **Desktop (>992px)**: Full 3-column layout
- **Tablet (768-992px)**: Adjusted message widths
- **Mobile (<768px)**: Stacked layout, full-width messages

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message input

## Events & Callbacks

### Reference Click

When a user clicks a source reference badge:

```typescript
onReferenceClick(reference: MessageReference): void {
  // Handle reference click
  // Navigate to PDF viewer, highlight page, etc.
}
```

## Performance Optimizations

1. **trackBy function**: Optimizes ngFor rendering
2. **Debounced scrolling**: Reduces scroll operations
3. **Change detection**: Manual detection for streaming updates
4. **Lazy loading**: Messages loaded only when needed

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader friendly

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Messages not displaying

- Check if `chatId` is provided
- Verify API endpoint returns correct data format
- Check browser console for errors

### Streaming not working

- Ensure backend sends proper SSE format with `data:` prefix
- Check CORS configuration allows streaming
- Verify EventSource or fetch API is supported

### Markdown not rendering

- Ensure `MarkdownModule.forRoot()` is in app config
- Check if markdown content is properly formatted
- Verify ngx-markdown is installed

### Styling issues

- Clear browser cache
- Check if PrimeNG theme is loaded
- Verify Bootstrap is imported in angular.json

## Future Enhancements

Potential improvements:

- [ ] Voice input support
- [ ] Message editing/deletion
- [ ] File attachments
- [ ] Code syntax highlighting themes
- [ ] Message reactions
- [ ] Multi-user chat support
- [ ] Message search/filter
- [ ] Export chat history

## Contributing

When making changes:

1. Update TypeScript interfaces if adding new fields
2. Maintain responsive design principles
3. Add error handling for new features
4. Update this README with new functionality

## License

Part of the RAG Chatbot project - see main project LICENSE.

## Support

For issues or questions:

- Check existing GitHub issues
- Create new issue with detailed description
- Include browser console errors
- Provide steps to reproduce

---

**Created with ❤️ using Angular 20, PrimeNG, and ngx-markdown**
