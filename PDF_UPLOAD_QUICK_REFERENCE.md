# PDF Upload Quick Reference Guide

## Quick Start

### 1. Run the Application

```bash
cd "/Users/divyanshusrivastava/Local RAG"
dotnet run --project API/API.csproj
```

### 2. Test the Upload Endpoint

#### Using cURL

```bash
# Replace {workspaceId} and {token} with actual values
curl -X POST "http://localhost:5000/api/workspaces/{workspaceId}/pdfs/upload" \
  -H "Authorization: Bearer {token}" \
  -F "files=@/path/to/document.pdf"
```

#### Using HTTPie

```bash
http --form POST "http://localhost:5000/api/workspaces/{workspaceId}/pdfs/upload" \
  Authorization:"Bearer {token}" \
  files@/path/to/document.pdf
```

#### Using Postman

1. Method: POST
2. URL: `http://localhost:5000/api/workspaces/{workspaceId}/pdfs/upload`
3. Headers: `Authorization: Bearer {token}`
4. Body: form-data
   - Key: `files`
   - Type: File
   - Value: Select PDF file(s)

## API Endpoint

```
POST /api/workspaces/{workspaceId}/pdfs/upload
```

## Request Requirements

| Requirement      | Value                       |
| ---------------- | --------------------------- |
| Authentication   | JWT Bearer Token (required) |
| Content-Type     | multipart/form-data         |
| Field Name       | `files`                     |
| File Type        | PDF only                    |
| Max File Size    | 50 MB per file              |
| Max Request Size | 500 MB total                |

## Response Structure

```typescript
interface BulkUploadResponseDto {
  results: UploadPDFResultDto[];
  successCount: number;
  failureCount: number;
  isOnlyPdfAutoSelected: boolean;
}

interface UploadPDFResultDto {
  id: string; // Guid
  fileName: string;
  fileSize: number; // bytes
  uploadedAt: string; // ISO 8601
  filePath: string;
  success: boolean;
  errorMessage?: string;
}
```

## Status Codes

| Code | Meaning                                |
| ---- | -------------------------------------- |
| 200  | Success (all files or partial success) |
| 400  | Bad Request (validation error)         |
| 401  | Unauthorized (invalid token)           |
| 404  | Not Found (workspace doesn't exist)    |
| 507  | Insufficient Storage (disk full)       |
| 500  | Internal Server Error                  |

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

### Environment Variables

```bash
export FileStorage__UploadPath="/var/app/uploads"
export FileStorage__MaxFileSizeMB=100
```

## File Storage Structure

```
uploads/
  └── {workspaceId}/
      ├── {fileId1}.pdf
      ├── {fileId2}.pdf
      └── {fileId3}.pdf
```

## Common Error Messages

| Error                          | Cause               | Solution                          |
| ------------------------------ | ------------------- | --------------------------------- |
| "No files were provided"       | Empty request       | Include files in form-data        |
| "Only PDF files are allowed"   | Wrong file type     | Upload .pdf files only            |
| "File size exceeds maximum"    | File > 50MB         | Reduce file size or adjust config |
| "Invalid authentication token" | Missing/invalid JWT | Login to get valid token          |
| "Workspace not found"          | Wrong workspace ID  | Use valid workspace ID            |
| "Insufficient disk space"      | Server disk full    | Free up disk space                |

## Validation Rules

### ✅ Valid PDF Files

- Content-Type: `application/pdf`
- Extension: `.pdf`
- Size: ≤ 50 MB
- Signature: Starts with `%PDF-`

### ❌ Invalid Files

- `.doc`, `.docx`, `.txt`, etc.
- Renamed files (e.g., `document.txt` renamed to `document.pdf`)
- Files > 50 MB
- Corrupted PDFs

## Database Table

```sql
-- PDFDocuments table schema
CREATE TABLE "PDFDocuments" (
    "Id" uuid PRIMARY KEY,
    "WorkspaceId" uuid NOT NULL,
    "FileName" text NOT NULL,
    "FilePath" text NOT NULL,
    "FileSize" bigint NOT NULL,
    "UploadedAt" timestamp NOT NULL,
    "IsSelected" boolean NOT NULL DEFAULT false,
    FOREIGN KEY ("WorkspaceId") REFERENCES "Workspaces"("Id") ON DELETE CASCADE
);
```

## Testing Checklist

- [ ] Upload single PDF file
- [ ] Upload multiple PDF files
- [ ] Upload file > 50MB (should fail)
- [ ] Upload non-PDF file (should fail)
- [ ] Upload without authentication (should return 401)
- [ ] Upload to non-existent workspace (should return 404)
- [ ] Verify file saved to disk
- [ ] Verify database record created
- [ ] Verify auto-selection when only one PDF
- [ ] Check response format matches specification

## Integration Points

### Frontend (Angular)

```typescript
// Service method
uploadPDFs(workspaceId: string, files: File[]): Observable<BulkUploadResponseDto> {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  return this.http.post<BulkUploadResponseDto>(
    `${this.apiUrl}/workspaces/${workspaceId}/pdfs/upload`,
    formData
  );
}
```

### Python LLM Service

```python
# Access uploaded PDF files
import os

def get_workspace_pdfs(workspace_id: str) -> List[str]:
    upload_path = os.path.join("uploads", str(workspace_id))
    return [os.path.join(upload_path, f)
            for f in os.listdir(upload_path)
            if f.endswith('.pdf')]
```

## Monitoring & Logging

### Log Messages

```
Information: User {UserId} is uploading {FileCount} file(s) to workspace {WorkspaceId}
Information: Upload completed: {SuccessCount} succeeded, {FailureCount} failed
Error: Insufficient disk space for upload to workspace {WorkspaceId}
Error: Unexpected error during PDF upload to workspace {WorkspaceId}
```

### Metrics to Monitor

- Upload success rate
- Average upload time
- Disk space usage
- Failed upload reasons
- File size distribution

## Troubleshooting

### Debug Mode

```bash
# Run with detailed logging
ASPNETCORE_ENVIRONMENT=Development dotnet run --project API/API.csproj
```

### Check File Permissions

```bash
# Ensure upload directory is writable
chmod 755 uploads/
```

### Verify Database

```sql
-- Check uploaded PDFs
SELECT "Id", "FileName", "FileSize", "UploadedAt"
FROM "PDFDocuments"
WHERE "WorkspaceId" = 'your-workspace-id';
```

## Performance Tips

1. **Batch Processing**: Upload multiple files in one request
2. **Compression**: Compress PDFs before upload if possible
3. **Network**: Use stable connection for large files
4. **Chunking**: For files > 50MB, consider implementing chunked upload

## Security Best Practices

1. Always use HTTPS in production
2. Rotate JWT tokens regularly
3. Monitor disk usage to prevent DoS
4. Implement rate limiting
5. Validate file content, not just extension
6. Use virus scanning for production

## Related Endpoints (To Be Implemented)

```
GET    /api/workspaces/{workspaceId}/pdfs
GET    /api/workspaces/{workspaceId}/pdfs/{pdfId}
DELETE /api/workspaces/{workspaceId}/pdfs/{pdfId}
PUT    /api/workspaces/{workspaceId}/pdfs/{pdfId}/select
```

## Support

- Swagger UI: http://localhost:5000/swagger
- Documentation: PDF_UPLOAD_API_DOCS.md
- Architecture: PDF_UPLOAD_ARCHITECTURE.md
- Implementation Details: PDF_UPLOAD_IMPLEMENTATION_SUMMARY.md
