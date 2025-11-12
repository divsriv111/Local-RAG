# Chat Interface - Visual Guide

## 🎨 Component Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat Interface Container                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Empty State (when no messages)              │   │
│  │                                                       │   │
│  │               📝 Comments Icon                        │   │
│  │              No messages yet                         │   │
│  │   Start a conversation by asking about your PDFs     │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  OR                                                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Messages List                        │   │
│  │  (Scrollable Container)                              │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────┐            │   │
│  │  │  Bot Message (Gray Bubble - Left)   │            │   │
│  │  │  Hello! How can I help you today?   │            │   │
│  │  │  10:30 AM                            │            │   │
│  │  └─────────────────────────────────────┘            │   │
│  │                                                       │   │
│  │            ┌──────────────────────────────────────┐  │   │
│  │            │  User Message (Blue Bubble - Right) │  │   │
│  │            │  What is AI about?                  │  │   │
│  │            │  10:31 AM                           │  │   │
│  │            └──────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────┐            │   │
│  │  │  Bot Message with Markdown          │            │   │
│  │  │  **AI** stands for Artificial       │            │   │
│  │  │  Intelligence. Here are key points: │            │   │
│  │  │  • Machine learning                  │            │   │
│  │  │  • Neural networks                   │            │   │
│  │  │  • Deep learning                     │            │   │
│  │  │  10:31 AM                            │            │   │
│  │  │  ─────────────────────────────       │            │   │
│  │  │  📄 Sources:                         │            │   │
│  │  │  [AI_Research.pdf - Page 5]         │            │   │
│  │  │  [ML_Basics.pdf - Page 12]          │            │   │
│  │  └─────────────────────────────────────┘            │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────┐            │   │
│  │  │  Typing Indicator (while streaming) │            │   │
│  │  │  ● ● ●  (animated bouncing)         │            │   │
│  │  └─────────────────────────────────────┘            │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                      Input Container                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⚠️ Please select at least one PDF to start chatting │   │
│  └─────────────────────────────────────────────────────┘   │
│  (Only shown when no PDFs selected)                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ LLM Model Selector     │  Message Input      │ Send │   │
│  │ ⚡ GPT-4 Turbo   ▼    │  Type your         │  ➤  │   │
│  │                       │  message here...    │      │   │
│  │                       │  500 / 4000         │      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Press Enter to send, Shift+Enter for new line              │
└─────────────────────────────────────────────────────────────┘
```

## 📱 Mobile Layout

```
┌─────────────────────────┐
│   Chat Interface        │
├─────────────────────────┤
│                         │
│  Messages List          │
│  (Stacked vertically)   │
│                         │
│  ┌─────────────────┐   │
│  │  Bot Message    │   │
│  │  Hello!         │   │
│  └─────────────────┘   │
│                         │
│      ┌──────────────┐  │
│      │User Message │  │
│      │Hi there!    │  │
│      └──────────────┘  │
│                         │
├─────────────────────────┤
│  Input Container        │
│  ┌───────────────────┐ │
│  │ Model Selector ▼  │ │
│  └───────────────────┘ │
│  ┌───────────────────┐ │
│  │ Type message...   │ │
│  └───────────────────┘ │
│  ┌───────────────────┐ │
│  │   Send Button     │ │
│  └───────────────────┘ │
└─────────────────────────┘
```

## 🎨 Color Scheme

### User Messages

- **Background**: Linear gradient `#007bff → #0056b3` (Blue)
- **Text**: White
- **Position**: Right-aligned
- **Border Radius**: `18px 18px 4px 18px` (rounded except bottom-right)

### Bot Messages

- **Background**: `#e9ecef` (Light gray)
- **Text**: `#212529` (Dark gray)
- **Position**: Left-aligned
- **Border Radius**: `18px 18px 18px 4px` (rounded except bottom-left)

### Streaming Message

- **Animation**: Subtle pulse effect
- **Cursor**: Blinking `▊` character
- **Opacity**: Fades between 1.0 and 0.8

### Typing Indicator

- **Dots**: 3 bouncing circles
- **Color**: Gray
- **Animation**: Staggered bounce (0s, 0.2s, 0.4s delay)

### Source References

- **Badge Background**: Gray/Secondary color
- **Hover**: Slight elevation with shadow
- **Icon**: 📄 PDF icon
- **Clickable**: Pointer cursor

## 🔤 Typography

### Message Content

- **User Messages**: 0.95rem, regular weight
- **Bot Messages**: 0.95rem, regular weight
- **Markdown Headers**: Bold, larger
- **Code Blocks**: Monospace font, slightly smaller

### Timestamps

- **Size**: 0.75rem
- **Color**: Translucent (80% opacity)
- **Format**: Relative time (e.g., "5m ago", "2h ago")

### Input

- **Placeholder**: 0.95rem, gray
- **Text**: 0.95rem, default color
- **Character Count**: 0.75rem, gray (red when > 90%)

## 📐 Spacing & Dimensions

### Messages Container

- **Padding**: 1.5rem (24px)
- **Gap between messages**: 1rem (16px)
- **Max width (user)**: 70% of container
- **Max width (bot)**: 75% of container

### Message Bubbles

- **Padding**: 0.875rem 1.125rem (14px 18px)
- **Shadow**: `0 2px 8px rgba(0,0,0,0.1)`
- **Hover Shadow**: `0 4px 12px rgba(0,0,0,0.15)`

### Input Container

- **Padding**: 1rem 1.5rem (16px 24px)
- **Border**: 1px solid #dee2e6 (top only)
- **Shadow**: `0 -2px 10px rgba(0,0,0,0.05)`

### Input Elements

- **Textarea Height**: Auto-resize, max 150px
- **Border Radius**: 24px
- **Send Button**: 48px diameter circle
- **Model Selector**: Min-width 180px

## ⚡ Animations

### Message Entry

```scss
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
duration: 0.3s ease-out;
```

### Streaming Cursor

```scss
@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}
duration: 1s step-end infinite;
```

### Typing Indicator

```scss
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}
Duration: 1.4s ease-in-out infinite
Stagger: 0.2s between dots
```

### Pulse (streaming)

```scss
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
duration: 1.5s ease-in-out infinite;
```

## 🎭 States

### Loading State

```
┌─────────────────────────┐
│         ⟳               │
│   Loading messages...   │
│                         │
└─────────────────────────┘
```

### Empty State

```
┌─────────────────────────┐
│         💬              │
│    No messages yet      │
│  Start a conversation   │
└─────────────────────────┘
```

### Error State

```
┌─────────────────────────┐
│  ❌ Message bubble      │
│  Failed to get response │
│  [Retry Button]         │
└─────────────────────────┘
```

### Disabled State

```
┌─────────────────────────┐
│  ⚠️ No PDFs selected    │
│  [Input is disabled]    │
└─────────────────────────┘
```

## 🖱️ Interactive Elements

### Hover Effects

- **Message Bubbles**: Slight lift (`translateY(-1px)`) + shadow increase
- **Source Badges**: Lift + shadow + tooltip
- **Send Button**: Scale (1.05) + shadow glow
- **Input**: Border color change + focus shadow

### Click/Touch Areas

- **Minimum**: 44x44px (WCAG guideline)
- **Send Button**: 48x48px
- **Reference Badges**: Adequate padding for touch
- **Model Dropdown**: Full clickable area

### Focus States

- **Input Textarea**: Blue border + shadow ring
- **Send Button**: Outline for keyboard navigation
- **Model Selector**: Dropdown opens with visual feedback

## 📊 Responsive Breakpoints

### Desktop (> 992px)

- Full side-by-side layout
- 70% max width for user messages
- 75% max width for bot messages
- Horizontal model selector + input + button

### Tablet (768px - 992px)

- Adjusted message widths (85%)
- Slightly reduced padding
- Same horizontal layout

### Mobile (< 768px)

- Messages: 90% max width
- **Stacked Layout**:
  1. Model selector (full width)
  2. Message input (full width)
  3. Send button (full width, rounded rectangle)
- Reduced padding and font sizes

## ♿ Accessibility Features

### ARIA Labels

- Messages list: `role="log"` `aria-live="polite"`
- Input: `aria-label="Message input"`
- Send button: `aria-label="Send message"`
- Model selector: Proper labeling

### Keyboard Navigation

- Tab through: Model selector → Input → Send button
- Enter: Send message (when input focused)
- Shift+Enter: New line
- Escape: Clear focus

### Screen Reader

- Message authors announced ("You said", "Assistant said")
- Timestamps announced in accessible format
- Source references with full PDF and page info
- Loading/streaming states announced

## 🎯 Component Hierarchy

```
ChatInterfaceComponent
├── Toast (notifications)
├── Loading Spinner (initial load)
└── Main Container
    ├── Messages Container
    │   ├── Empty State OR
    │   └── Messages List
    │       ├── Message Wrapper (ngFor)
    │       │   └── Message Bubble
    │       │       ├── Content (text or markdown)
    │       │       ├── Timestamp
    │       │       └── References (if bot message)
    │       └── Typing Indicator (if streaming)
    └── Input Container
        ├── No PDF Warning (conditional)
        └── Input Row
            ├── Model Selector (PrimeNG Select)
            ├── Message Input Wrapper
            │   ├── Textarea (PrimeNG)
            │   └── Character Count
            └── Send Button

```

## 🔄 Data Flow

```
User Types Message
      ↓
[Send Button Clicked]
      ↓
Add User Message to UI (optimistic)
      ↓
Create Streaming Bot Message Placeholder
      ↓
Call ChatService.sendMessageWithFetch()
      ↓
Backend Streams Response
      ↓
[Token by Token]
      ↓
Update Bot Message Content in Real-time
      ↓
Collect Source References
      ↓
[Stream Complete]
      ↓
Save Bot Message to Database
      ↓
Update UI with Saved Message
```

## 📝 Example Interactions

### Sending a Message

1. User types in textarea
2. Character count updates in real-time
3. User presses Enter (or clicks Send)
4. User message appears instantly (blue bubble, right)
5. Gray bot message placeholder appears (left)
6. Typing indicator shows (bouncing dots)
7. Typing indicator disappears
8. Bot response streams in word-by-word
9. Blinking cursor at end of streaming text
10. Source references appear below message
11. Stream complete, cursor disappears
12. Message saved to database

### Clicking a Reference

1. User hovers over badge → tooltip appears
2. User clicks badge
3. Event handler called with reference data
4. (Implement: Navigate to PDF viewer at page)

### Model Selection

1. User clicks model dropdown
2. Options appear with descriptions
3. User selects model
4. Dropdown shows selected model with icon
5. Future messages use selected model

---

## 🎨 Design Philosophy

The chat interface follows these principles:

1. **Familiar**: Modeled after iMessage for instant recognition
2. **Clean**: Minimal UI, focus on content
3. **Responsive**: Works beautifully on all devices
4. **Performant**: Smooth animations, efficient rendering
5. **Accessible**: WCAG 2.1 AA compliant
6. **Informative**: Clear states, helpful feedback
7. **Delightful**: Subtle animations, smooth interactions

---

This visual guide should help you understand the component's layout, styling, and behavior at a glance!
