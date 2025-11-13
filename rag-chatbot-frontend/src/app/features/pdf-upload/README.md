# PDF Upload Component

A fully-featured Angular component for uploading, managing, and selecting PDF documents with drag-and-drop support, progress tracking, and responsive design.

## Features

✅ **Drag-and-Drop Upload**: Intuitive file upload with drag-and-drop support  
✅ **Multiple File Selection**: Upload multiple PDFs simultaneously  
✅ **File Validation**: Automatic validation for file type (PDF only) and size (max 50MB)  
✅ **Real-time Progress**: Upload progress bar for each file (0-100%)  
✅ **PDF Selection**: Checkbox-based selection with visual highlighting  
✅ **Auto-selection**: Automatically selects PDF if only one is uploaded  
✅ **Delete Functionality**: Remove PDFs with confirmation  
✅ **Responsive Design**: Mobile-friendly with collapsible panel  
✅ **Toast Notifications**: Success/error feedback using PrimeNG Toast  
✅ **Cancel Upload**: Ability to cancel ongoing uploads

## Installation

### 1. Copy Files

Copy the following files to your Angular project:

```
src/app/
├── core/
│   ├── models/
│   │   └── pdf-document.model.ts
│   └── services/
│       └── pdf.service.ts
└── features/
    └── pdf-upload/
        ├── pdf-upload.component.ts
        ├── pdf-upload.component.html
        ├── pdf-upload.component.scss
        └── pdf-upload.module.ts (optional, for module-based apps)
```

### 2. Install Dependencies

Ensure you have the required PrimeNG modules installed:

```bash
npm install primeng primeicons bootstrap
```

### 3. Configure Styles

Add to your `angular.json`:

```json
"styles": [
  "node_modules/primeng/resources/themes/lara-light-blue/theme.css",
  "node_modules/primeng/resources/primeng.min.css",
  "node_modules/primeicons/primeicons.css",
  "node_modules/bootstrap/dist/css/bootstrap.min.css",
  "src/styles.scss"
]
```

### 4. Update Environment

Ensure your environment file has the API URL:

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000',
};
```

## Usage

### Basic Usage (Standalone Component - Angular 20+)

```typescript
import { Component } from '@angular/core';
import { PdfUploadComponent } from './features/pdf-upload/pdf-upload.component';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [PdfUploadComponent, ToastModule],
  template: `
    <div class="container">
      <div class="row">
        <div class="col-lg-3">
          <app-pdf-upload
            [workspaceId]="workspaceId"
            (selectedPdfsChange)="onPdfSelectionChange($event)"
            (pdfListChange)="onPdfListChange($event)"
          ></app-pdf-upload>
        </div>
        <div class="col-lg-9">
          <!-- Chat interface here -->
        </div>
      </div>
    </div>
    <p-toast></p-toast>
  `,
})
export class WorkspaceDetailComponent {
  workspaceId = 'your-workspace-id';

  onPdfSelectionChange(selectedPdfIds: string[]) {
    console.log('Selected PDFs:', selectedPdfIds);
  }

  onPdfListChange(pdfs: PdfDocument[]) {
    console.log('PDF list updated:', pdfs);
  }
}
```

### Module-Based Usage (Older Angular Versions)

```typescript
// app.module.ts
import { PdfUploadModule } from './features/pdf-upload/pdf-upload.module';

@NgModule({
  imports: [
    // ... other imports
    PdfUploadModule,
  ],
})
export class AppModule {}
```

## API Reference

### Component Inputs

| Input         | Type     | Description                                                    |
| ------------- | -------- | -------------------------------------------------------------- |
| `workspaceId` | `string` | **Required**. The workspace ID to associate uploaded PDFs with |

### Component Outputs

| Output               | Type                          | Description                                            |
| -------------------- | ----------------------------- | ------------------------------------------------------ |
| `selectedPdfsChange` | `EventEmitter<string[]>`      | Emits array of selected PDF IDs when selection changes |
| `pdfListChange`      | `EventEmitter<PdfDocument[]>` | Emits updated PDF list after upload/delete operations  |

### PdfDocument Interface

```typescript
interface PdfDocument {
  id: string; // Unique identifier
  fileName: string; // Original file name
  fileSize: number; // File size in bytes
  uploadedAt: Date; // Upload timestamp
  workspaceId: string; // Associated workspace ID
  isSelected: boolean; // Selection state
  filePath?: string; // Optional file path on server
}
```

### PdfService Methods

```typescript
class PdfService {
  // Upload files with progress tracking
  upload(workspaceId: string, files: File[]): Observable<HttpEvent<any>>;

  // Get all PDFs for a workspace
  getAll(workspaceId: string): Observable<PdfDocument[]>;

  // Delete a PDF by ID
  delete(pdfId: string): Observable<void>;

  // Update selected PDF IDs
  updateSelection(pdfIds: string[]): void;

  // Get current selection
  getSelectedPdfIds(): Set<string>;

  // Clear all selections
  clearSelection(): void;

  // Add/remove/toggle individual selection
  addToSelection(pdfId: string): void;
  removeFromSelection(pdfId: string): void;
  toggleSelection(pdfId: string): void;
}
```

## Backend API Requirements

The component expects the following API endpoints:

### 1. Upload PDFs

```http
POST /api/workspaces/{workspaceId}/pdfs/upload
Content-Type: multipart/form-data

Request Body: FormData with files[] array

Response:
{
  "uploadedFiles": [
    {
      "id": "guid",
      "fileName": "document.pdf",
      "fileSize": 1024000,
      "uploadedAt": "2024-01-01T12:00:00Z",
      "workspaceId": "workspace-guid",
      "isSelected": false
    }
  ]
}
```

### 2. Get All PDFs

```http
GET /api/workspaces/{workspaceId}/pdfs

Response: PdfDocument[]
```

### 3. Delete PDF

```http
DELETE /api/pdfs/{pdfId}

Response: 204 No Content
```

## Customization

### Styling

Override component styles in your global `styles.scss`:

```scss
app-pdf-upload {
  // Change primary color
  --primary-color: #3b82f6;

  // Customize selected item background
  .pdf-item.selected {
    background: #eff6ff;
    border-color: #3b82f6;
  }

  // Modify upload area
  .upload-drop-area {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
}
```

### Configuration

Modify component properties:

```typescript
// Change max file size (default: 50MB)
maxFileSize = 100 * 1024 * 1024; // 100MB

// Change accepted file types
acceptedFileTypes = '.pdf,.doc,.docx';
```

## Responsive Behavior

- **Desktop (>992px)**: Full sidebar layout with all features visible
- **Tablet (768px-992px)**: Compact view with smaller spacing
- **Mobile (<768px)**: Collapsible panel, stacked layout, always-visible delete buttons

## Validation Rules

- ✅ Only PDF files accepted
- ✅ Maximum 50MB per file
- ✅ Multiple files can be uploaded simultaneously
- ✅ File type checked via MIME type and extension

## Error Handling

The component handles the following error scenarios:

- **Invalid file type**: Shows warning toast, file is not uploaded
- **File too large**: Shows warning toast, file is not uploaded
- **Upload failure**: Shows error toast with details
- **Delete failure**: Shows error toast, maintains current state
- **Network errors**: Caught and displayed to user

## Accessibility

- ✅ Keyboard navigation support
- ✅ ARIA labels on interactive elements
- ✅ Screen reader friendly
- ✅ Focus indicators
- ✅ Semantic HTML structure

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### PDFs not uploading

1. Check backend API is running and accessible
2. Verify CORS is enabled on the backend
3. Check browser console for network errors
4. Ensure `workspaceId` is provided

### Selection not working

1. Verify `PdfService` is imported correctly
2. Check that `MessageService` is provided
3. Ensure FormsModule is imported

### Styling issues

1. Verify PrimeNG theme CSS is loaded
2. Check Bootstrap CSS is imported
3. Clear browser cache
4. Check for CSS conflicts

## Examples

### Using with Chat Component

```typescript
@Component({
  selector: 'app-chat-workspace',
  template: `
    <div class="workspace-layout">
      <div class="sidebar">
        <app-pdf-upload
          [workspaceId]="workspaceId"
          (selectedPdfsChange)="selectedPdfIds = $event"
        ></app-pdf-upload>
      </div>
      <div class="chat-area">
        <app-chat-interface
          [workspaceId]="workspaceId"
          [selectedPdfIds]="selectedPdfIds"
        ></app-chat-interface>
      </div>
    </div>
  `,
})
export class ChatWorkspaceComponent {
  workspaceId = 'workspace-123';
  selectedPdfIds: string[] = [];
}
```

### Programmatic Selection

```typescript
export class MyComponent {
  @ViewChild(PdfUploadComponent) pdfUpload!: PdfUploadComponent;

  selectAllPdfs() {
    const allIds = this.pdfUpload.uploadedPdfs.map((pdf) => pdf.id);
    this.pdfService.updateSelection(allIds);
  }

  clearSelection() {
    this.pdfService.clearSelection();
  }
}
```

## License

MIT License - Free to use in personal and commercial projects

## Support

For issues or questions, please refer to the main project documentation or create an issue in the repository.
