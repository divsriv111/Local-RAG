# PDF Upload Component - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Ensure Dependencies are Installed

```bash
# Already installed based on your package.json:
# - primeng@20.3.0
# - primeicons@7.0.0
# - bootstrap@5.3.8
```

### Step 2: Add Toast to Your App Component

**app.component.ts:**

```typescript
import { Component } from '@angular/core';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ToastModule /* ...other imports */],
  providers: [MessageService],
  template: `
    <router-outlet></router-outlet>
    <p-toast position="top-right"></p-toast>
  `,
})
export class AppComponent {}
```

### Step 3: Use in Your Component

**workspace-detail.component.ts:**

```typescript
import { Component } from '@angular/core';
import { PdfUploadComponent } from '../pdf-upload/pdf-upload.component';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [PdfUploadComponent],
  template: `
    <div class="container-fluid">
      <div class="row">
        <div class="col-lg-3">
          <app-pdf-upload
            [workspaceId]="workspaceId"
            (selectedPdfsChange)="selectedPdfIds = $event"
          ></app-pdf-upload>
        </div>
        <div class="col-lg-9">
          <!-- Your chat interface here -->
        </div>
      </div>
    </div>
  `,
})
export class WorkspaceDetailComponent {
  workspaceId = 'your-workspace-id';
  selectedPdfIds: string[] = [];
}
```

### Step 4: Verify Environment Configuration

**src/environments/environment.ts:**

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000', // ✅ Already configured
};
```

## 📂 Files Created

All files have been created in your project:

```
✅ /core/models/pdf-document.model.ts
✅ /core/services/pdf.service.ts
✅ /features/pdf-upload/pdf-upload.component.ts
✅ /features/pdf-upload/pdf-upload.component.html
✅ /features/pdf-upload/pdf-upload.component.scss
✅ /features/pdf-upload/pdf-upload.module.ts (optional)
✅ /features/pdf-upload/README.md
✅ /features/pdf-upload/pdf-upload.examples.ts
```

## 🎯 Key Features

| Feature                     | Status |
| --------------------------- | ------ |
| Drag & Drop Upload          | ✅     |
| Multiple File Selection     | ✅     |
| Real-time Progress (0-100%) | ✅     |
| PDF Selection Checkboxes    | ✅     |
| Auto-select Single PDF      | ✅     |
| Delete with Confirmation    | ✅     |
| File Validation (PDF, 50MB) | ✅     |
| Toast Notifications         | ✅     |
| Responsive Design           | ✅     |
| Mobile-Friendly             | ✅     |

## 🔌 Backend API Endpoints Required

You need to implement these 3 endpoints in your ASP.NET Core backend:

### 1. Upload PDFs

```http
POST /api/workspaces/{workspaceId}/pdfs/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

Request: FormData with files[]
Response: 200 OK with uploaded file details
```

### 2. Get All PDFs

```http
GET /api/workspaces/{workspaceId}/pdfs
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "id": "guid",
    "fileName": "document.pdf",
    "fileSize": 1024000,
    "uploadedAt": "2024-01-01T12:00:00Z",
    "workspaceId": "workspace-guid",
    "isSelected": false
  }
]
```

### 3. Delete PDF

```http
DELETE /api/pdfs/{pdfId}
Authorization: Bearer {token}

Response: 204 No Content
```

## 🎨 Customization

### Change Colors

```scss
// Add to your global styles.scss
app-pdf-upload {
  --primary-color: #your-color;

  .pdf-item.selected {
    background: #your-selected-bg;
  }
}
```

### Change Max File Size

```typescript
// In pdf-upload.component.ts
maxFileSize = 100 * 1024 * 1024; // Change to 100MB
```

## 🐛 Troubleshooting

### Issue: PDFs not uploading

**Solution**: Check browser console for errors. Verify backend API is running on `http://localhost:5000`

### Issue: Selection not working

**Solution**: Ensure `MessageService` is provided in your app component

### Issue: Styles not applied

**Solution**: Verify PrimeNG theme CSS is loaded in angular.json

### Issue: TypeScript errors

**Solution**: Run `npm install` to ensure all dependencies are installed

## 📱 Responsive Behavior

- **Desktop (>992px)**: Full sidebar (300px width)
- **Tablet (768-992px)**: Compact layout
- **Mobile (<768px)**: Full-width collapsible panel

## 💡 Tips

1. **Always provide workspaceId**: The component requires it to function
2. **Add Toast to app**: Required for notifications
3. **Handle selectedPdfsChange**: Use this to enable/disable chat functionality
4. **Check network tab**: If uploads fail, check the Network tab in DevTools

## 🔗 Component API

### Inputs

```typescript
@Input() workspaceId: string;  // Required!
```

### Outputs

```typescript
@Output() selectedPdfsChange: EventEmitter<string[]>;
@Output() pdfListChange: EventEmitter<PdfDocument[]>;
```

### Methods (via PdfService)

```typescript
pdfService.upload(workspaceId, files);
pdfService.getAll(workspaceId);
pdfService.delete(pdfId);
pdfService.updateSelection(pdfIds);
```

## ✅ Next Steps

1. **Test the component**: Import and use in a workspace component
2. **Implement backend**: Create the 3 required API endpoints
3. **Test file upload**: Upload a PDF and verify it appears in the list
4. **Test selection**: Select PDFs and verify the IDs are emitted
5. **Test deletion**: Delete a PDF and verify it's removed

## 📚 Documentation

- **Full Documentation**: See `README.md` in the pdf-upload folder
- **Examples**: See `pdf-upload.examples.ts` for 4 detailed usage examples
- **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md` for complete details

---

**Ready to Go!** 🎉

The component is fully implemented and ready to use. Just import it in your workspace component and provide a workspaceId.

Need help? Check the README.md or examples file for detailed guidance.
