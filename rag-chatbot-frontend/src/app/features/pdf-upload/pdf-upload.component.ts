import { Component, EventEmitter, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEventType } from '@angular/common/http';
import { Subject, takeUntil } from 'rxjs';
import { MessageService } from 'primeng/api';
import { PanelModule } from 'primeng/panel';
import { FileUploadModule } from 'primeng/fileupload';
import { ProgressBarModule } from 'primeng/progressbar';
import { CheckboxModule } from 'primeng/checkbox';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { PdfService } from '../../core/services/pdf.service';
import { PdfDocument, PdfUploadProgress } from '../../core/models/pdf-document.model';

@Component({
  selector: 'app-pdf-upload',
  templateUrl: './pdf-upload.component.html',
  styleUrls: ['./pdf-upload.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    PanelModule,
    FileUploadModule,
    ProgressBarModule,
    CheckboxModule,
    ButtonModule,
    TooltipModule,
  ],
  providers: [MessageService],
})
export class PdfUploadComponent implements OnInit, OnDestroy {
  @Input() workspaceId: string = '';
  @Output() selectedPdfsChange = new EventEmitter<string[]>();
  @Output() pdfListChange = new EventEmitter<PdfDocument[]>();

  uploadedPdfs: PdfDocument[] = [];
  selectedPdfIds = new Set<string>();
  uploadProgress: Map<string, PdfUploadProgress> = new Map();
  isUploading = false;
  maxFileSize = 50 * 1024 * 1024; // 50MB in bytes
  acceptedFileTypes = '.pdf';

  private destroy$ = new Subject<void>();

  constructor(private pdfService: PdfService, private messageService: MessageService) {}

  ngOnInit(): void {
    this.loadPdfs();

    // Subscribe to selection changes from service
    this.pdfService.selectedPdfIds$.pipe(takeUntil(this.destroy$)).subscribe((selectedIds) => {
      this.selectedPdfIds = selectedIds;
      this.selectedPdfsChange.emit(Array.from(selectedIds));
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load PDFs for the current workspace
   */
  loadPdfs(): void {
    if (!this.workspaceId) {
      return;
    }

    this.pdfService.getAll(this.workspaceId).subscribe({
      next: (pdfs) => {
        this.uploadedPdfs = pdfs;
        this.pdfListChange.emit(pdfs);

        // Auto-select if only one PDF
        if (pdfs.length === 1 && this.selectedPdfIds.size === 0) {
          this.selectPdf(pdfs[0].id, true);
        }
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load PDFs',
        });
        console.error('Error loading PDFs:', error);
      },
    });
  }

  /**
   * Handle file selection from FileUpload component
   */
  onFileSelect(event: any): void {
    const files: File[] = event.files || event.currentFiles;

    if (!files || files.length === 0) {
      return;
    }

    // Validate files
    const validFiles = this.validateFiles(files);

    if (validFiles.length > 0) {
      this.uploadFiles(validFiles);
    }
  }

  /**
   * Validate selected files
   */
  private validateFiles(files: File[]): File[] {
    const validFiles: File[] = [];

    for (const file of files) {
      // Check file type
      if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
        this.messageService.add({
          severity: 'warn',
          summary: 'Invalid File Type',
          detail: `${file.name} is not a PDF file`,
        });
        continue;
      }

      // Check file size
      if (file.size > this.maxFileSize) {
        this.messageService.add({
          severity: 'warn',
          summary: 'File Too Large',
          detail: `${file.name} exceeds 50MB limit`,
        });
        continue;
      }

      validFiles.push(file);
    }

    return validFiles;
  }

  /**
   * Upload files to the server
   */
  uploadFiles(files: File[]): void {
    this.isUploading = true;

    // Initialize progress tracking for each file
    files.forEach((file) => {
      this.uploadProgress.set(file.name, {
        file,
        progress: 0,
        uploading: true,
      });
    });

    this.pdfService.upload(this.workspaceId, files).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress) {
          // Update progress for all files (assuming equal distribution)
          const percentDone = event.total ? Math.round((100 * event.loaded) / event.total) : 0;
          files.forEach((file) => {
            const progress = this.uploadProgress.get(file.name);
            if (progress) {
              progress.progress = percentDone;
            }
          });
        } else if (event.type === HttpEventType.Response) {
          // Upload complete
          this.handleUploadComplete(files, event.body);
        }
      },
      error: (error) => {
        this.handleUploadError(files, error);
      },
    });
  }

  /**
   * Handle successful upload completion
   */
  private handleUploadComplete(files: File[], response: any): void {
    this.isUploading = false;

    // Clear upload progress
    files.forEach((file) => {
      this.uploadProgress.delete(file.name);
    });

    this.messageService.add({
      severity: 'success',
      summary: 'Upload Successful',
      detail: `${files.length} file(s) uploaded successfully`,
    });

    // Refresh PDF list
    this.loadPdfs();
  }

  /**
   * Handle upload error
   */
  private handleUploadError(files: File[], error: any): void {
    this.isUploading = false;

    files.forEach((file) => {
      const progress = this.uploadProgress.get(file.name);
      if (progress) {
        progress.uploading = false;
        progress.error = error.message || 'Upload failed';
      }
    });

    this.messageService.add({
      severity: 'error',
      summary: 'Upload Failed',
      detail: error.error?.message || 'Failed to upload files',
    });
  }

  /**
   * Cancel ongoing upload
   */
  cancelUpload(fileName: string): void {
    this.uploadProgress.delete(fileName);

    if (this.uploadProgress.size === 0) {
      this.isUploading = false;
    }
  }

  /**
   * Handle PDF selection change
   */
  onPdfSelectionChange(pdfId: string, isChecked: boolean): void {
    this.selectPdf(pdfId, isChecked);
  }

  /**
   * Select or deselect a PDF
   */
  private selectPdf(pdfId: string, isSelected: boolean): void {
    if (isSelected) {
      this.pdfService.addToSelection(pdfId);
    } else {
      this.pdfService.removeFromSelection(pdfId);
    }
  }

  /**
   * Check if a PDF is selected
   */
  isPdfSelected(pdfId: string): boolean {
    return this.selectedPdfIds.has(pdfId);
  }

  /**
   * Delete a PDF
   */
  deletePdf(pdfId: string, event: Event): void {
    event.stopPropagation();

    if (confirm('Are you sure you want to delete this PDF?')) {
      this.pdfService.delete(pdfId).subscribe({
        next: () => {
          this.messageService.add({
            severity: 'success',
            summary: 'Deleted',
            detail: 'PDF deleted successfully',
          });

          // Remove from selection if selected
          if (this.selectedPdfIds.has(pdfId)) {
            this.pdfService.removeFromSelection(pdfId);
          }

          // Refresh list
          this.loadPdfs();
        },
        error: (error) => {
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete PDF',
          });
          console.error('Error deleting PDF:', error);
        },
      });
    }
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Format upload date for display
   */
  formatDate(date: Date): string {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  }

  /**
   * Get upload progress percentage
   */
  getUploadProgress(fileName: string): number {
    return this.uploadProgress.get(fileName)?.progress || 0;
  }

  /**
   * Check if file is currently uploading
   */
  isFileUploading(fileName: string): boolean {
    return this.uploadProgress.get(fileName)?.uploading || false;
  }

  /**
   * Get array of files being uploaded
   */
  getUploadingFiles(): PdfUploadProgress[] {
    return Array.from(this.uploadProgress.values());
  }

  /**
   * Check if any PDFs are selected
   */
  hasSelectedPdfs(): boolean {
    return this.selectedPdfIds.size > 0;
  }

  /**
   * Get count of selected PDFs
   */
  getSelectedCount(): number {
    return this.selectedPdfIds.size;
  }
}
