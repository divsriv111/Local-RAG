import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import {
  ChatHistory,
  ChatHistoryResponse,
  CreateChatHistoryRequest,
} from '../models/chat-history.model';

@Injectable({
  providedIn: 'root',
})
export class ChatHistoryService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  /**
   * Get all chat histories for a workspace
   * @param workspaceId - The workspace ID
   * @param includeArchived - Whether to include archived chats (default: false)
   * @returns Observable of chat history array
   */
  getAll(workspaceId: string, includeArchived: boolean = false): Observable<ChatHistory[]> {
    let params = new HttpParams();
    if (includeArchived) {
      params = params.set('includeArchived', 'true');
    }

    return this.http
      .get<ChatHistoryResponse[]>(`${this.apiUrl}/workspaces/${workspaceId}/chats`, { params })
      .pipe(map((responses) => responses.map((response) => this.mapToChatHistory(response))));
  }

  /**
   * Create a new chat history for a workspace
   * @param workspaceId - The workspace ID
   * @returns Observable of created chat history
   */
  create(workspaceId: string): Observable<ChatHistory> {
    const request: CreateChatHistoryRequest = { workspaceId };

    return this.http
      .post<ChatHistoryResponse>(`${this.apiUrl}/workspaces/${workspaceId}/chats`, request)
      .pipe(map((response) => this.mapToChatHistory(response)));
  }

  /**
   * Archive a chat history
   * @param chatId - The chat history ID
   * @returns Observable of void
   */
  archive(chatId: string): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/chats/${chatId}/archive`, {});
  }

  /**
   * Delete a chat history
   * @param chatId - The chat history ID
   * @returns Observable of void
   */
  delete(chatId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/chats/${chatId}`);
  }

  /**
   * Get a single chat history by ID
   * @param chatId - The chat history ID
   * @returns Observable of chat history
   */
  getById(chatId: string): Observable<ChatHistory> {
    return this.http
      .get<ChatHistoryResponse>(`${this.apiUrl}/chats/${chatId}`)
      .pipe(map((response) => this.mapToChatHistory(response)));
  }

  /**
   * Map API response to ChatHistory model
   * @param response - The API response
   * @returns ChatHistory object
   */
  private mapToChatHistory(response: ChatHistoryResponse): ChatHistory {
    return {
      id: response.id,
      workspaceId: response.workspaceId,
      name: response.name,
      firstQuery: response.firstQuery,
      createdAt: new Date(response.createdAt),
      isArchived: response.isArchived,
      messageCount: response.messageCount,
      updatedAt: response.updatedAt ? new Date(response.updatedAt) : undefined,
    };
  }
}
