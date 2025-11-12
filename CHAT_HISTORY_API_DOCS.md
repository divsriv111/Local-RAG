# Chat History Management API Documentation

## Overview

Complete implementation of chat history and message management endpoints following Clean Architecture and CQRS patterns with MediatR.

## Implemented Endpoints

### 1. POST /api/workspaces/{workspaceId}/chats

**Create New Chat History**

- **Authorization**: Required (JWT Bearer token)
- **Description**: Creates a new chat history for a workspace
- **Auto-generated**: Name defaults to "New Chat" (can be updated later with first query)
- **Response**: 201 Created with ChatHistoryDto
- **Authorization Check**: Verifies user owns the workspace

**Response Example**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "workspaceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "New Chat",
  "firstQuery": "",
  "createdAt": "2025-11-11T10:30:00Z",
  "isArchived": false,
  "messageCount": 0
}
```

---

### 2. GET /api/workspaces/{workspaceId}/chats

**Get All Chat Histories for Workspace**

- **Authorization**: Required (JWT Bearer token)
- **Query Parameters**:
  - `includeArchived` (bool, default: false) - Include archived chats
- **Description**: Returns list of chats sorted by createdAt descending
- **Response**: 200 OK with list of ChatHistoryListItemDto
- **Authorization Check**: Verifies user owns the workspace

**Response Example**:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Project Discussion",
    "createdAt": "2025-11-11T10:30:00Z",
    "isArchived": false,
    "messageCount": 15
  },
  {
    "id": "2ea74f53-4606-3451-a2eb-1b852e55bea5",
    "name": "Technical Review",
    "createdAt": "2025-11-10T14:20:00Z",
    "isArchived": false,
    "messageCount": 8
  }
]
```

---

### 3. GET /api/chats/{chatId}/messages

**Get All Messages for a Chat**

- **Authorization**: Required (JWT Bearer token)
- **Query Parameters**:
  - `pageNumber` (int, default: 1, min: 1)
  - `pageSize` (int, default: 50, min: 1, max: 100)
- **Description**: Returns paginated list of messages ordered by timestamp
- **Response**: 200 OK with PaginatedMessagesDto
- **Authorization Check**: Verifies user owns the workspace containing the chat

**Response Example**:

```json
{
  "messages": [
    {
      "id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
      "chatHistoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "content": "What is machine learning?",
      "isUserMessage": true,
      "timestamp": "2025-11-11T10:31:00Z",
      "references": null
    },
    {
      "id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
      "chatHistoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "content": "Machine learning is a subset of artificial intelligence...",
      "isUserMessage": false,
      "timestamp": "2025-11-11T10:31:05Z",
      "references": "[{\"pdf\": \"ml-basics.pdf\", \"page\": 3}]"
    }
  ],
  "totalCount": 15,
  "pageNumber": 1,
  "pageSize": 50,
  "totalPages": 1
}
```

---

### 4. POST /api/chats/{chatId}/messages

**Add New Message to Chat**

- **Authorization**: Required (JWT Bearer token)
- **Request Body**: CreateMessageDto
  - `content` (string, required) - Message content
  - `isUserMessage` (bool, required) - True for user, false for assistant
  - `references` (string, optional) - JSON string with source references
- **Response**: 201 Created with MessageDto
- **Authorization Check**: Verifies user owns the workspace containing the chat

**Request Example**:

```json
{
  "content": "Explain neural networks in simple terms",
  "isUserMessage": true,
  "references": null
}
```

**Response Example**:

```json
{
  "id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
  "chatHistoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "content": "Explain neural networks in simple terms",
  "isUserMessage": true,
  "timestamp": "2025-11-11T10:35:00Z",
  "references": null
}
```

---

### 5. PUT /api/chats/{chatId}/archive

**Archive Chat History**

- **Authorization**: Required (JWT Bearer token)
- **Description**: Sets isArchived to true
- **Response**: 200 OK with updated ChatHistoryDto
- **Authorization Check**: Verifies user owns the workspace containing the chat

**Response Example**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "workspaceId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Project Discussion",
  "firstQuery": "What is the project scope?",
  "createdAt": "2025-11-11T10:30:00Z",
  "isArchived": true,
  "messageCount": 15
}
```

---

### 6. DELETE /api/chats/{chatId}

**Delete Chat History**

- **Authorization**: Required (JWT Bearer token)
- **Description**: Hard deletes chat and all associated messages (cascade)
- **Response**: 204 No Content
- **Authorization Check**: Verifies user owns the workspace containing the chat

---

## Architecture Components

### DTOs (Application/DTOs/)

- **ChatHistoryDto**: Full chat history with message count
- **ChatHistoryListItemDto**: Simplified for list views
- **MessageDto**: Single message with references
- **CreateMessageDto**: Request DTO for creating messages
- **PaginatedMessagesDto**: Paginated message list with metadata

### Commands (Application/Features/ChatHistories/Commands/)

1. **CreateChatHistoryCommand** + Handler

   - Creates new chat with default name "New Chat"
   - Verifies workspace ownership

2. **ArchiveChatHistoryCommand** + Handler

   - Sets isArchived flag to true
   - Returns updated chat with message count

3. **DeleteChatHistoryCommand** + Handler
   - Cascades delete to all messages
   - Returns boolean success status

### Commands (Application/Features/Messages/Commands/)

1. **CreateMessageCommand** + Handler
   - Creates message with timestamp
   - Supports references as JSON string
   - Verifies chat ownership through workspace

### Queries (Application/Features/ChatHistories/Queries/)

1. **GetChatHistoriesByWorkspaceQuery** + Handler
   - Filters by workspace ID
   - Optional includeArchived flag
   - Sorted by createdAt descending
   - Includes message count for each chat

### Queries (Application/Features/Messages/Queries/)

1. **GetMessagesByChatHistoryQuery** + Handler
   - Pagination support (pageNumber, pageSize)
   - Ordered by timestamp ascending
   - Returns metadata (totalCount, totalPages)

### Controller (API/Controllers/)

- **ChatHistoriesController**
  - All 6 REST endpoints
  - JWT Bearer authentication required
  - Claims-based user ID extraction
  - Comprehensive error handling
  - Proper HTTP status codes

### Repository Updates

Updated **IRepository** and **Repository** implementation to support:

- `GetAllAsQueryable()`: For LINQ queries
- `Update(T entity)`: Synchronous update
- `Delete(T entity)`: Synchronous delete

## Security Features

- ✅ JWT Bearer token authentication on all endpoints
- ✅ User ID extraction from claims (ClaimTypes.NameIdentifier)
- ✅ Workspace ownership verification
- ✅ Chat history ownership verification (via workspace)
- ✅ 403 Forbidden for unauthorized access
- ✅ 404 Not Found for non-existent resources

## Error Handling

- **400 Bad Request**: Invalid input (empty content, etc.)
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: User doesn't own the resource
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Unexpected errors with details

## Testing

Test file created: `API/ChatHistories.http`

- Includes all 9 endpoint tests
- Variables for baseUrl, token, workspaceId, chatId
- Example requests with sample data

## Notes

- Chat name generation from first query is stubbed as "New Chat" (LLM integration pending)
- References stored as JSON string for flexibility
- Pagination max page size limited to 100 for performance
- Messages ordered chronologically (oldest first)
- Chat histories ordered by creation date (newest first)
- Cascade delete implemented manually in handler

## Future Enhancements

- [ ] Auto-generate chat name from first user query using LLM
- [ ] Soft delete option for chat histories
- [ ] Update chat name endpoint
- [ ] Search/filter messages by content
- [ ] Export chat history as PDF/JSON
- [ ] Real-time updates via SignalR
