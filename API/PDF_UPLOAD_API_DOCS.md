# PDF Upload API Documentation

## Overview

The PDF Upload API endpoint allows authenticated users to upload multiple PDF files to a specific workspace. The endpoint includes robust validation, error handling, and automatic file management.

## Endpoint

```
POST /api/workspaces/{workspaceId}/pdfs/upload
```

## Authentication

This endpoint requires JWT Bearer token authentication.

```
Authorization: Bearer <your_jwt_token>
```

## Request

### Headers

- `Authorization`: Bearer token (required)
- `Content-Type`: multipart/form-data (required)

### Path Parameters

- `workspaceId` (Guid): The ID of the workspace where PDFs will be uploaded

### Form Data

- `files` (IFormFileCollection): One or more PDF files to upload

### Constraints

- Maximum file size per file: **50 MB** (configurable in appsettings.json)
- Maximum total request size: **500 MB**
- Allowed file types: **PDF only**
- File validation includes:
  - Content-Type check (must be `application/pdf`)
  - File extension check (must be `.pdf`)
  - PDF signature verification (magic bytes: `%PDF-`)

## Response

### Success Response (200 OK)

```json
{
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "fileName": "document.pdf",
      "fileSize": 1048576,
      "uploadedAt": "2025-11-11T10:30:00Z",
      "filePath": "uploads/workspace-id/file-id.pdf",
      "success": true,
      "errorMessage": null
    }
  ],
  "successCount": 1,
  "failureCount": 0,
  "isOnlyPdfAutoSelected": true
}
```

### Partial Success Response (200 OK)

When some files succeed and others fail:

```json
{
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "fileName": "valid.pdf",
      "fileSize": 1048576,
      "uploadedAt": "2025-11-11T10:30:00Z",
      "filePath": "uploads/workspace-id/file-id.pdf",
      "success": true,
      "errorMessage": null
    },
    {
      "id": "7fb85f64-5717-4562-b3fc-2c963f66afb7",
      "fileName": "invalid.txt",
      "fileSize": 2048,
      "uploadedAt": "2025-11-11T10:30:00Z",
      "filePath": "",
      "success": false,
      "errorMessage": "Only PDF files are allowed."
    }
  ],
  "successCount": 1,
  "failureCount": 1,
  "isOnlyPdfAutoSelected": false
}
```

### Error Responses

#### 400 Bad Request

No files provided:

```json
{
  "message": "No files were provided for upload."
}
```

All files failed validation:

```json
{
  "results": [...],
  "successCount": 0,
  "failureCount": 2,
  "isOnlyPdfAutoSelected": false
}
```

#### 401 Unauthorized

```json
{
  "message": "Invalid authentication token."
}
```

#### 404 Not Found

```json
{
  "message": "Workspace not found or you don't have access to it."
}
```

#### 507 Insufficient Storage

```json
{
  "message": "Insufficient disk space to complete the upload.",
  "error": "Insufficient disk space to save the file."
}
```

#### 500 Internal Server Error

```json
{
  "message": "An unexpected error occurred during file upload.",
  "error": "Detailed error message"
}
```

## Features

### 1. Multiple File Upload

Upload multiple PDF files in a single request. Each file is processed independently.

### 2. Comprehensive Validation

- **File Type**: Only PDF files are accepted
- **File Size**: Maximum 50 MB per file (configurable)
- **PDF Signature**: Verifies the file is actually a PDF by checking magic bytes
- **Content Type**: Validates the MIME type is `application/pdf`

### 3. Auto-Selection

If a PDF is the **only** file in the workspace after upload, it will be automatically selected (marked as `IsSelected = true`).

### 4. Error Handling

Each file upload is handled independently. If one file fails, others can still succeed. Detailed error messages are provided for each failure.

### 5. File Organization

Files are stored in a workspace-specific directory structure:

```
uploads/
  ├── {workspaceId}/
      ├── {fileId1}.pdf
      ├── {fileId2}.pdf
      └── ...
```

### 6. Database Integration

Successful uploads are automatically recorded in the PostgreSQL database with the following metadata:

- Unique file ID (Guid)
- Original filename
- File size in bytes
- Upload timestamp (UTC)
- File path on disk
- Selection status

## Configuration

### appsettings.json

```json
{
  "FileStorage": {
    "UploadPath": "uploads",
    "MaxFileSizeMB": 50
  }
}
```

### Environment Variables (Optional)

```bash
FileStorage__UploadPath=/var/app/uploads
FileStorage__MaxFileSizeMB=100
```

## Examples

### cURL Example

```bash
curl -X POST "http://localhost:5000/api/workspaces/{workspaceId}/pdfs/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### JavaScript/Fetch Example

```javascript
const formData = new FormData();
formData.append("files", file1); // File object from input
formData.append("files", file2);

const response = await fetch(
  `http://localhost:5000/api/workspaces/${workspaceId}/pdfs/upload`,
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  }
);

const result = await response.json();
console.log(result);
```

### Angular/TypeScript Example

```typescript
uploadPDFs(workspaceId: string, files: File[]): Observable<BulkUploadResponseDto> {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  return this.http.post<BulkUploadResponseDto>(
    `${this.apiUrl}/workspaces/${workspaceId}/pdfs/upload`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${this.authService.getToken()}`
      },
      reportProgress: true, // For progress tracking
      observe: 'events'
    }
  );
}
```

## Validation Error Messages

| Error Condition             | Error Message                                           |
| --------------------------- | ------------------------------------------------------- |
| No file provided            | "File is empty or not provided."                        |
| File too large              | "File size exceeds the maximum allowed size of X MB."   |
| Wrong file type (extension) | "Only PDF files are allowed."                           |
| Wrong content type          | "Invalid file type. Only PDF files are allowed."        |
| Invalid PDF signature       | "File does not appear to be a valid PDF document."      |
| Disk space issue            | "Disk error: Insufficient disk space to save the file." |
| Generic upload error        | "Upload failed: {exception message}"                    |

## Performance Considerations

1. **Chunked Upload**: The endpoint supports streaming upload for large files
2. **Async Operations**: All file I/O operations are async
3. **Independent Processing**: Files are processed independently to avoid cascading failures
4. **Connection Pooling**: Database operations use EF Core connection pooling

## Security Considerations

1. **Authentication Required**: All requests must include a valid JWT token
2. **User Authorization**: The system verifies workspace ownership
3. **File Type Validation**: Multiple layers of PDF validation
4. **Path Traversal Prevention**: File paths are sanitized
5. **Disk Space Checking**: Prevents disk exhaustion attacks

## Future Enhancements

- [ ] Real-time upload progress via SignalR
- [ ] Support for chunked/resumable uploads
- [ ] Thumbnail generation
- [ ] OCR text extraction on upload
- [ ] Duplicate file detection
- [ ] Virus scanning integration
- [ ] Cloud storage support (AWS S3, Azure Blob)

## Troubleshooting

### Issue: "File does not appear to be a valid PDF document"

**Solution**: Ensure the file is a genuine PDF and not renamed from another format.

### Issue: "Insufficient disk space"

**Solution**: Free up disk space on the server or configure a different storage location.

### Issue: Request timeout

**Solution**: For large files, increase request timeout in Kestrel configuration:

```csharp
builder.WebHost.ConfigureKestrel(options => {
    options.Limits.RequestHeadersTimeout = TimeSpan.FromMinutes(10);
});
```

### Issue: File size limit exceeded

**Solution**: Adjust `MaxFileSizeMB` in appsettings.json or implement chunked uploads.

## Related Endpoints

- `GET /api/workspaces/{workspaceId}/pdfs` - List all PDFs in workspace
- `DELETE /api/workspaces/{workspaceId}/pdfs/{pdfId}` - Delete a PDF
- `PUT /api/workspaces/{workspaceId}/pdfs/{pdfId}/select` - Select/deselect a PDF

## Support

For issues or questions, please refer to:

- API Documentation: http://localhost:5000/swagger
- GitHub Repository: [Your Repo URL]
- Issue Tracker: [Your Issue Tracker URL]
