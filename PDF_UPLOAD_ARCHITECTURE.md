# PDF Upload Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Angular)                            │
│  - Drag & Drop UI                                                   │
│  - File Selection                                                   │
│  - Progress Display                                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP POST (multipart/form-data)
                            │ Authorization: Bearer <token>
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      API LAYER (Controllers)                         │
│  PDFsController.cs                                                  │
│  - POST /api/workspaces/{id}/pdfs/upload                           │
│  - Authentication & Authorization                                   │
│  - Request Validation                                               │
│  - Response Formatting                                              │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ MediatR Command
                            ↓
┌─────────────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (Commands & Handlers)                 │
│  UploadPDFsCommand                                                  │
│  UploadPDFsCommandHandler                                           │
│  - Business Logic                                                   │
│  - Orchestration                                                    │
│  - Auto-selection Logic                                             │
└───┬────────────┬────────────┬──────────────────────────────────┬────┘
    │            │            │                                  │
    ↓            ↓            ↓                                  ↓
┌──────────┐ ┌──────────┐ ┌──────────────┐              ┌──────────────┐
│  File    │ │  File    │ │  Repository  │              │  UnitOfWork  │
│Validation│ │ Storage  │ │  (Generic)   │              │              │
│ Service  │ │ Service  │ │              │              │              │
└──────────┘ └──────────┘ └──────────────┘              └──────────────┘
     │            │              │                              │
     ↓            ↓              ↓                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
│  FileValidationService                                              │
│  - ValidatePdfFileAsync()                                           │
│  - IsPdfFile()                                                      │
│  - VerifyPdfSignatureAsync()                                        │
│                                                                     │
│  FileStorageService                                                 │
│  - SaveFileAsync()                                                  │
│  - DeleteFileAsync()                                                │
│  - EnsureDirectoryExistsAsync()                                     │
│                                                                     │
│  Repository<PDFDocument>                                            │
│  - AddAsync()                                                       │
│  - GetAllAsync()                                                    │
│                                                                     │
│  UnitOfWork                                                         │
│  - SaveChangesAsync()                                               │
└───────────┬────────────────────────────┬─────────────────────────────┘
            │                            │
            ↓                            ↓
    ┌──────────────┐          ┌─────────────────┐
    │  File System │          │   PostgreSQL    │
    │   (uploads/) │          │    Database     │
    │              │          │  PDFDocuments   │
    │  workspace1/ │          │    Table        │
    │  ├─file1.pdf │          │                 │
    │  └─file2.pdf │          │                 │
    └──────────────┘          └─────────────────┘
```

## Request Flow

```
1. Client sends HTTP POST with files
         ↓
2. PDFsController receives request
   - Validates authentication (JWT)
   - Extracts workspace ID and user ID
   - Creates UploadPDFsCommand
         ↓
3. MediatR dispatches to UploadPDFsCommandHandler
         ↓
4. Handler verifies workspace exists
         ↓
5. For each file:
   a. FileValidationService validates:
      - File size ≤ 50MB
      - Content-Type = application/pdf
      - Extension = .pdf
      - PDF signature check (%PDF-)
   b. If valid:
      - FileStorageService saves to disk
      - Creates PDFDocument entity
         ↓
6. Handler saves all entities to database
         ↓
7. Auto-selection logic:
   - If workspace has only 1 PDF, mark as selected
         ↓
8. UnitOfWork commits transaction
         ↓
9. Response sent back to client with results
```

## Data Flow

```
┌──────────────┐
│ IFormFile[]  │  (Client Upload)
└──────┬───────┘
       │
       ↓
┌──────────────────────────┐
│ Validation               │
│ - Type check             │
│ - Size check             │
│ - Signature check        │
└──────┬───────────────────┘
       │ (if valid)
       ↓
┌──────────────────────────┐
│ File Storage             │
│ uploads/{workspace}/{id} │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ Database Record          │
│ PDFDocument entity       │
│ - Id, FileName, Path     │
│ - Size, UploadedAt       │
│ - IsSelected             │
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ Response DTO             │
│ BulkUploadResponseDto    │
│ - Results[]              │
│ - SuccessCount           │
│ - FailureCount           │
└──────────────────────────┘
```

## Component Responsibilities

### API Layer (PDFsController)

- HTTP request/response handling
- Authentication/Authorization
- Input validation
- Logging
- Error translation

### Application Layer (Command/Handler)

- Business logic orchestration
- Domain rules (auto-selection)
- Transaction management
- Error handling

### Infrastructure Layer (Services)

- File I/O operations
- File validation
- Database access
- External dependencies

### Domain Layer (Entities)

- Business entities (PDFDocument)
- Domain interfaces

## Error Handling Strategy

```
┌───────────────┐
│   Exception   │
└───────┬───────┘
        │
        ├─→ UnauthorizedAccessException → 401 Unauthorized
        │
        ├─→ InvalidOperationException (Workspace) → 404 Not Found
        │
        ├─→ IOException (Disk Space) → 507 Insufficient Storage
        │
        ├─→ Validation Errors → Individual file failure (in results)
        │
        └─→ Other Exceptions → 500 Internal Server Error
```

## Security Layers

```
1. Authentication (JWT)
   ↓
2. Authorization (Workspace Ownership)
   ↓
3. File Type Validation
   ↓
4. File Size Validation
   ↓
5. PDF Signature Verification
   ↓
6. Disk Space Check
   ↓
7. Path Sanitization
```

## Performance Optimizations

1. **Async I/O**: All file operations are async
2. **Streaming**: Direct stream from HTTP to file system
3. **Buffered Writes**: 8KB buffer for file writes
4. **Independent Processing**: Files don't block each other
5. **Connection Pooling**: EF Core manages DB connections
6. **No Memory Loading**: Files never loaded entirely into memory
