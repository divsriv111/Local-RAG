export interface PdfDocument {
  id: string;
  fileName: string;
  fileSize: number;
  uploadedAt: Date;
  workspaceId: string;
  isSelected: boolean;
  filePath?: string;
}

export interface PdfUploadProgress {
  file: File;
  progress: number;
  uploading: boolean;
  error?: string;
  uploadedDocument?: PdfDocument;
}
