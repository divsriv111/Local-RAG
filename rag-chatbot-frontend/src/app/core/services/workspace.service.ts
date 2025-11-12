import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Workspace, CreateWorkspaceDto, UpdateWorkspaceDto } from '../models/workspace.models';

@Injectable({
  providedIn: 'root',
})
export class WorkspaceService {
  private readonly apiUrl = `${environment.apiUrl}/api/workspaces`;

  constructor(private http: HttpClient) {}

  /**
   * Get all workspaces for the authenticated user with optional search filter
   * @param search Optional search string to filter workspaces by name
   * @returns Observable of Workspace array sorted by createdAt descending
   */
  getAll(search?: string): Observable<Workspace[]> {
    let params = new HttpParams();
    if (search) {
      params = params.set('search', search);
    }
    params = params.set('sortBy', 'createdAt');
    params = params.set('sortOrder', 'desc');

    return this.http.get<Workspace[]>(this.apiUrl, { params });
  }

  /**
   * Get workspace by ID
   * @param id Workspace ID
   * @returns Observable of Workspace with associated chat histories and PDFs
   */
  getById(id: string): Observable<Workspace> {
    return this.http.get<Workspace>(`${this.apiUrl}/${id}`);
  }

  /**
   * Create a new workspace
   * @param name Workspace name
   * @returns Observable of created Workspace
   */
  create(name: string): Observable<Workspace> {
    const dto: CreateWorkspaceDto = { name };
    return this.http.post<Workspace>(this.apiUrl, dto);
  }

  /**
   * Update workspace name
   * @param id Workspace ID
   * @param name New workspace name
   * @returns Observable of updated Workspace
   */
  update(id: string, name: string): Observable<Workspace> {
    const dto: UpdateWorkspaceDto = { name };
    return this.http.put<Workspace>(`${this.apiUrl}/${id}`, dto);
  }

  /**
   * Delete workspace and all associated data
   * @param id Workspace ID
   * @returns Observable of void
   */
  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
