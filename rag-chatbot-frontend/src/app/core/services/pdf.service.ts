import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable, BehaviorSubject, map, catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PdfDocument } from '../models/pdf-document.model';

@Injectable({
  providedIn: 'root',
})
export class PdfService {
  private apiUrl = `${environment.apiUrl}/api`;
  private selectedPdfIdsSubject = new BehaviorSubject<Set<string>>(new Set());
  public selectedPdfIds$ = this.selectedPdfIdsSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Upload multiple PDF files to a workspace with progress tracking
   * @param workspaceId The workspace ID to upload files to
   * @param files Array of files to upload
   * @returns Observable of HttpEvent for progress tracking
   */
  upload(workspaceId: string, files: File[]): Observable<HttpEvent<any>> {
    const formData = new FormData();

    files.forEach((file, index) => {
      formData.append(`files`, file, file.name);
    });

    const req = new HttpRequest(
      'POST',
      `${this.apiUrl}/workspaces/${workspaceId}/pdfs/upload`,
      formData,
      {
        reportProgress: true,
      }
    );

    return this.http.request(req).pipe(
      catchError((error) => {
        console.error('PDF upload error:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get all PDFs for a workspace
   * @param workspaceId The workspace ID
   * @returns Observable of PdfDocument array
   */
  getAll(workspaceId: string): Observable<PdfDocument[]> {
    return this.http.get<PdfDocument[]>(`${this.apiUrl}/workspaces/${workspaceId}/pdfs`).pipe(
      map((pdfs) =>
        pdfs.map((pdf) => ({
          ...pdf,
          uploadedAt: new Date(pdf.uploadedAt),
        }))
      ),
      catchError((error) => {
        console.error('Error fetching PDFs:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Delete a PDF document
   * @param pdfId The PDF ID to delete
   * @returns Observable of void
   */
  delete(pdfId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/pdfs/${pdfId}`).pipe(
      catchError((error) => {
        console.error('Error deleting PDF:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update the selected PDF IDs
   * @param pdfIds Array of selected PDF IDs
   */
  updateSelection(pdfIds: string[]): void {
    this.selectedPdfIdsSubject.next(new Set(pdfIds));
  }

  /**
   * Get currently selected PDF IDs
   * @returns Set of selected PDF IDs
   */
  getSelectedPdfIds(): Set<string> {
    return this.selectedPdfIdsSubject.value;
  }

  /**
   * Clear all selections
   */
  clearSelection(): void {
    this.selectedPdfIdsSubject.next(new Set());
  }

  /**
   * Add a PDF to selection
   * @param pdfId The PDF ID to add
   */
  addToSelection(pdfId: string): void {
    const currentSelection = new Set(this.selectedPdfIdsSubject.value);
    currentSelection.add(pdfId);
    this.selectedPdfIdsSubject.next(currentSelection);
  }

  /**
   * Remove a PDF from selection
   * @param pdfId The PDF ID to remove
   */
  removeFromSelection(pdfId: string): void {
    const currentSelection = new Set(this.selectedPdfIdsSubject.value);
    currentSelection.delete(pdfId);
    this.selectedPdfIdsSubject.next(currentSelection);
  }

  /**
   * Toggle PDF selection
   * @param pdfId The PDF ID to toggle
   */
  toggleSelection(pdfId: string): void {
    const currentSelection = new Set(this.selectedPdfIdsSubject.value);
    if (currentSelection.has(pdfId)) {
      currentSelection.delete(pdfId);
    } else {
      currentSelection.add(pdfId);
    }
    this.selectedPdfIdsSubject.next(currentSelection);
  }
}
