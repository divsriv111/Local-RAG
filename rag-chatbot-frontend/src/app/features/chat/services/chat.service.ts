import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, Subject, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Message, SendMessageRequest, StreamingChunk } from '../models/message.model';
import { environment } from '../../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apiUrl = environment.apiUrl || 'http://localhost:5000/api';
  private streamingSubject = new Subject<StreamingChunk>();

  constructor(private http: HttpClient) {}

  /**
   * Get all messages for a specific chat
   */
  getMessages(chatId: string): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/chats/${chatId}/messages`).pipe(
      map((messages) =>
        messages.map((msg) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }))
      ),
      catchError((error) => {
        console.error('Error fetching messages:', error);
        return throwError(() => new Error('Failed to fetch messages'));
      })
    );
  }

  /**
   * Send a message and get streaming response
   */
  sendMessage(request: SendMessageRequest): Observable<StreamingChunk> {
    const streamSubject = new Subject<StreamingChunk>();

    // Create EventSource for Server-Sent Events
    const eventSource = new EventSource(this.buildStreamUrl(request), {
      withCredentials: true,
    });

    eventSource.onmessage = (event) => {
      try {
        const chunk: StreamingChunk = JSON.parse(event.data);
        streamSubject.next(chunk);

        // Close connection when done
        if (chunk.type === 'done' || chunk.type === 'error') {
          eventSource.close();
          streamSubject.complete();
        }
      } catch (error) {
        console.error('Error parsing streaming chunk:', error);
        streamSubject.error(new Error('Failed to parse streaming response'));
        eventSource.close();
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      streamSubject.error(new Error('Streaming connection failed'));
      eventSource.close();
    };

    return streamSubject.asObservable();
  }

  /**
   * Alternative: Send message using HTTP POST with streaming via fetch API
   */
  sendMessageWithFetch(request: SendMessageRequest): Observable<StreamingChunk> {
    const streamSubject = new Subject<StreamingChunk>();
    const token = localStorage.getItem('token');

    fetch(`${this.apiUrl}/llm/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error('Response body is not readable');
        }

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            streamSubject.complete();
            break;
          }

          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true });

          // Parse Server-Sent Events format: "data: {...}\n\n"
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonData = line.substring(6).trim();
                if (jsonData) {
                  const parsedChunk: StreamingChunk = JSON.parse(jsonData);
                  streamSubject.next(parsedChunk);

                  if (parsedChunk.type === 'done' || parsedChunk.type === 'error') {
                    streamSubject.complete();
                    return;
                  }
                }
              } catch (e) {
                console.error('Error parsing chunk:', e);
              }
            }
          }
        }
      })
      .catch((error) => {
        console.error('Fetch error:', error);
        streamSubject.error(error);
      });

    return streamSubject.asObservable();
  }

  /**
   * Create a new message in the database
   */
  createMessage(chatId: string, message: Partial<Message>): Observable<Message> {
    return this.http.post<Message>(`${this.apiUrl}/chats/${chatId}/messages`, message).pipe(
      map((msg) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })),
      catchError((error) => {
        console.error('Error creating message:', error);
        return throwError(() => new Error('Failed to create message'));
      })
    );
  }

  /**
   * Build streaming URL with query parameters for EventSource
   */
  private buildStreamUrl(request: SendMessageRequest): string {
    const params = new URLSearchParams({
      query: request.query,
      workspaceId: request.workspaceId,
      chatHistoryId: request.chatHistoryId,
      llmModel: request.llmModel,
      selectedPdfIds: request.selectedPdfIds.join(','),
    });

    const token = localStorage.getItem('token');
    if (token) {
      params.append('token', token);
    }

    return `${this.apiUrl}/llm/query/stream?${params.toString()}`;
  }

  /**
   * Retry failed message
   */
  retryMessage(request: SendMessageRequest): Observable<StreamingChunk> {
    return this.sendMessageWithFetch(request);
  }
}
