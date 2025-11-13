# PDF Upload Component - Integration Checklist

## ✅ Pre-Integration Verification

### Files Created

- [x] `/core/models/pdf-document.model.ts` - Type definitions
- [x] `/core/services/pdf.service.ts` - PDF service with HTTP methods
- [x] `/features/pdf-upload/pdf-upload.component.ts` - Main component (TypeScript)
- [x] `/features/pdf-upload/pdf-upload.component.html` - Template
- [x] `/features/pdf-upload/pdf-upload.component.scss` - Styles
- [x] `/features/pdf-upload/pdf-upload.module.ts` - Module (optional)
- [x] `/features/pdf-upload/README.md` - Full documentation
- [x] `/features/pdf-upload/pdf-upload.examples.ts` - Usage examples

### Documentation Created

- [x] `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- [x] `PDF_UPLOAD_QUICK_START.md` - Quick start guide

---

## 📋 Step-by-Step Integration

### Step 1: Verify Environment ✅

Your environment is already configured:

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000', // ✅ Already set
};
```

### Step 2: Add Toast Module to App Component

**File: `src/app/app.component.ts`**

```typescript
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    ToastModule, // ← Add this
  ],
  providers: [
    MessageService, // ← Add this
  ],
  template: `
    <router-outlet />
    <p-toast position="top-right"></p-toast>
    <!-- Add this -->
  `,
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'rag-chatbot-frontend';
}
```

**Action Items:**

- [ ] Import `ToastModule` from 'primeng/toast'
- [ ] Import `MessageService` from 'primeng/api'
- [ ] Add `ToastModule` to imports array
- [ ] Add `MessageService` to providers array
- [ ] Add `<p-toast>` element to template

### Step 3: Create or Update Workspace Detail Component

**Option A: Create New Component (Recommended)**

```bash
# Run this command if you don't have a workspace detail component
ng generate component features/workspace-detail --standalone
```

**Option B: Use Existing Component**

If you already have a workspace/chat component, proceed to Step 4.

### Step 4: Import PDF Upload Component

**File: Your workspace component (e.g., `workspace-detail.component.ts`)**

```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { PdfUploadComponent } from '../pdf-upload/pdf-upload.component';
import { PdfDocument } from '../../core/models/pdf-document.model';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [
    CommonModule,
    PdfUploadComponent, // ← Import the component
  ],
  template: `
    <div class="workspace-container">
      <div class="container-fluid p-0">
        <div class="row g-0">
          <!-- Left Sidebar: Chat History (Optional) -->
          <div class="col-lg-2 d-none d-lg-block border-end">
            <!-- Chat history list here -->
          </div>

          <!-- Center: Chat Interface -->
          <div class="col-lg-7 col-md-8">
            <div class="chat-panel p-3">
              <h5>Chat Interface</h5>
              <div *ngIf="selectedPdfIds.length === 0" class="alert alert-warning">
                <i class="pi pi-exclamation-triangle me-2"></i>
                Please select PDFs from the sidebar to start chatting
              </div>
              <!-- Your chat interface here -->
            </div>
          </div>

          <!-- Right Sidebar: PDF Upload -->
          <div class="col-lg-3 col-md-4 border-start">
            <app-pdf-upload
              [workspaceId]="workspaceId"
              (selectedPdfsChange)="onPdfSelectionChange($event)"
              (pdfListChange)="onPdfListChange($event)"
            ></app-pdf-upload>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      .workspace-container {
        height: 100vh;
        overflow: hidden;
      }

      .chat-panel {
        height: 100vh;
        overflow-y: auto;
      }

      @media (max-width: 768px) {
        .workspace-container {
          height: auto;
        }

        .chat-panel {
          height: auto;
          min-height: 60vh;
        }
      }
    `,
  ],
})
export class WorkspaceDetailComponent implements OnInit {
  workspaceId: string = '';
  selectedPdfIds: string[] = [];
  uploadedPdfs: PdfDocument[] = [];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Get workspace ID from route params
    this.route.params.subscribe((params) => {
      this.workspaceId = params['id'] || '';
    });
  }

  onPdfSelectionChange(selectedIds: string[]): void {
    this.selectedPdfIds = selectedIds;
    console.log('Selected PDF IDs:', selectedIds);

    // Enable/disable chat functionality based on selection
    // Your logic here
  }

  onPdfListChange(pdfs: PdfDocument[]): void {
    this.uploadedPdfs = pdfs;
    console.log('PDF list updated:', pdfs);
  }
}
```

**Action Items:**

- [ ] Import `PdfUploadComponent`
- [ ] Import `PdfDocument` model
- [ ] Add component to imports array
- [ ] Add `<app-pdf-upload>` to template
- [ ] Bind `[workspaceId]` input
- [ ] Handle `(selectedPdfsChange)` event
- [ ] Handle `(pdfListChange)` event (optional)

### Step 5: Update Routing (if needed)

**File: `app.routes.ts` or your routing file**

```typescript
import { Routes } from '@angular/router';
import { WorkspaceDetailComponent } from './features/workspace-detail/workspace-detail.component';

export const routes: Routes = [
  // ... other routes
  {
    path: 'workspace/:id',
    component: WorkspaceDetailComponent,
  },
];
```

**Action Items:**

- [ ] Add route for workspace detail component
- [ ] Test navigation to `/workspace/{id}`

---

## 🔧 Backend API Implementation

### Required Endpoints

You need to implement these 3 endpoints in your ASP.NET Core backend:

#### 1. Upload PDFs Endpoint

**File: `API/Controllers/PDFsController.cs`**

```csharp
[HttpPost("/api/workspaces/{workspaceId}/pdfs/upload")]
[Authorize]
public async Task<IActionResult> UploadPdfs(
    string workspaceId,
    [FromForm] IFormFileCollection files)
{
    // Validate workspace exists and user has access
    // Validate files (type, size)
    // Save files to disk/cloud storage
    // Save metadata to database
    // Return uploaded file details

    return Ok(new { uploadedFiles = /* list of PDFs */ });
}
```

**Action Items:**

- [ ] Create `PDFsController.cs`
- [ ] Implement upload endpoint
- [ ] Add file validation
- [ ] Save files to storage
- [ ] Save metadata to PostgreSQL

#### 2. Get All PDFs Endpoint

```csharp
[HttpGet("/api/workspaces/{workspaceId}/pdfs")]
[Authorize]
public async Task<IActionResult> GetAllPdfs(string workspaceId)
{
    // Validate workspace access
    // Query PDFs from database
    // Return list

    return Ok(pdfs);
}
```

**Action Items:**

- [ ] Implement GET endpoint
- [ ] Add authorization check
- [ ] Return PDF list

#### 3. Delete PDF Endpoint

```csharp
[HttpDelete("/api/pdfs/{pdfId}")]
[Authorize]
public async Task<IActionResult> DeletePdf(string pdfId)
{
    // Validate PDF exists and user has access
    // Delete file from storage
    // Delete metadata from database

    return NoContent();
}
```

**Action Items:**

- [ ] Implement DELETE endpoint
- [ ] Add authorization check
- [ ] Delete file and metadata

---

## 🧪 Testing Checklist

### Frontend Testing

- [ ] **Component Loads**: Navigate to workspace and verify component appears
- [ ] **File Selection**: Click "Choose PDFs" and select a PDF file
- [ ] **Drag & Drop**: Drag a PDF file into the upload area
- [ ] **Upload Progress**: Verify progress bar shows 0-100%
- [ ] **Upload Success**: Check success toast notification appears
- [ ] **PDF List**: Verify uploaded PDF appears in the list
- [ ] **File Metadata**: Check file name, size, and date are correct
- [ ] **Selection**: Click checkbox to select PDF
- [ ] **Selection Highlight**: Verify selected PDF has different background
- [ ] **Selection Event**: Check console for selectedPdfsChange event
- [ ] **Auto-Select**: Upload single PDF and verify it's auto-selected
- [ ] **Delete**: Click delete button and confirm deletion
- [ ] **Delete Confirmation**: Verify confirmation dialog appears
- [ ] **Multiple Upload**: Select multiple PDFs and upload simultaneously
- [ ] **Validation - Type**: Try uploading a .txt file (should fail)
- [ ] **Validation - Size**: Try uploading a file > 50MB (should fail)
- [ ] **Cancel Upload**: Start upload and click cancel button
- [ ] **Error Handling**: Stop backend and verify error toast appears

### Responsive Testing

- [ ] **Desktop (1920px)**: Full three-column layout
- [ ] **Laptop (1366px)**: Proper spacing and layout
- [ ] **Tablet (768px)**: Responsive layout adjustments
- [ ] **Mobile (375px)**: Collapsible panel, full width
- [ ] **Rotation**: Test portrait and landscape on mobile

### Browser Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## 🐛 Common Issues & Solutions

### Issue 1: "Cannot find module '@angular/common/http'"

**Solution:** HttpClient is already imported in the service. No action needed.

### Issue 2: Toast notifications not appearing

**Solution:**

1. Verify `MessageService` is provided in app.component.ts
2. Verify `<p-toast>` is in app.component template
3. Check PrimeNG Toast CSS is loaded

### Issue 3: File upload returns 404

**Solution:**

1. Verify backend is running on port 5000
2. Check API endpoint URL in environment.ts
3. Verify CORS is enabled on backend

### Issue 4: PDFs not loading after upload

**Solution:**

1. Check browser Network tab for API errors
2. Verify GET endpoint is implemented
3. Check workspace ID is correct

### Issue 5: Styles not applied

**Solution:**

1. Verify PrimeNG theme CSS in angular.json
2. Clear browser cache
3. Restart dev server (`ng serve`)

---

## 📊 Verification Checklist

### Code Verification

- [x] All TypeScript files compile without errors
- [x] No console errors in browser
- [x] All imports resolve correctly
- [x] Component is standalone (Angular 20)
- [x] Service uses HttpClient correctly
- [x] Models have correct types

### Functionality Verification

- [ ] Can upload PDF files
- [ ] Can select/deselect PDFs
- [ ] Can delete PDFs
- [ ] Selection state persists
- [ ] Events emit correctly
- [ ] Toast notifications work
- [ ] Progress tracking works
- [ ] Auto-select works

### UI/UX Verification

- [ ] Responsive on all screen sizes
- [ ] Hover effects work
- [ ] Selected items highlighted
- [ ] Icons display correctly
- [ ] Tooltips appear on hover
- [ ] Empty state shows when no PDFs
- [ ] Warning shows when no selection

---

## 🚀 Deployment Checklist

### Before Deploying

- [ ] All tests passing
- [ ] Backend API implemented
- [ ] Environment variables configured
- [ ] CORS enabled for production domain
- [ ] File upload limits configured on backend
- [ ] Authentication working
- [ ] Error logging configured

### Production Considerations

- [ ] Use production API URL in environment.prod.ts
- [ ] Enable HTTPS for file uploads
- [ ] Configure file storage (AWS S3, Azure Blob, etc.)
- [ ] Set appropriate file size limits
- [ ] Implement rate limiting on upload endpoint
- [ ] Add virus scanning for uploaded files
- [ ] Configure CDN for file delivery
- [ ] Set up monitoring and alerts

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - Complete documentation
- **pdf-upload.examples.ts** - 4 usage examples
- **IMPLEMENTATION_SUMMARY.md** - Full implementation details
- **PDF_UPLOAD_QUICK_START.md** - This guide

### External Links

- [PrimeNG FileUpload](https://primeng.org/fileupload)
- [Angular HttpClient](https://angular.io/guide/http)
- [RxJS BehaviorSubject](https://rxjs.dev/api/index/class/BehaviorSubject)
- [Bootstrap Grid](https://getbootstrap.com/docs/5.3/layout/grid/)

---

## ✅ Final Checklist

Before marking as complete:

- [ ] All files created and saved
- [ ] Toast module added to app component
- [ ] Component imported in workspace component
- [ ] Backend API endpoints documented
- [ ] Testing checklist reviewed
- [ ] Documentation read and understood
- [ ] Ready for first test upload

---

## 🎉 Success Criteria

Your integration is complete when:

1. ✅ You can navigate to a workspace
2. ✅ The PDF upload panel appears on the right
3. ✅ You can drag & drop or select PDF files
4. ✅ Upload progress shows in real-time
5. ✅ Uploaded PDFs appear in the list
6. ✅ You can select/deselect PDFs with checkboxes
7. ✅ Selected PDFs are highlighted
8. ✅ You can delete PDFs
9. ✅ Toast notifications appear for all actions
10. ✅ Component is responsive on mobile

---

**Need Help?**

- Check the README.md for detailed API reference
- Review pdf-upload.examples.ts for usage patterns
- Consult IMPLEMENTATION_SUMMARY.md for technical details

**Ready to integrate!** 🚀
