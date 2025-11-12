import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  ElementRef,
  AfterViewChecked,
  Input,
  ChangeDetectorRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import { Subject, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

// PrimeNG Imports
import { TextareaModule } from 'primeng/textarea';
import { ButtonModule } from 'primeng/button';
import { SelectModule } from 'primeng/select';
import { BadgeModule } from 'primeng/badge';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ToastModule } from 'primeng/toast';
import { TooltipModule } from 'primeng/tooltip';
import { MessageService } from 'primeng/api';

// Services and Models
import { ChatService } from '../../services/chat.service';
import {
  Message,
  LlmModel,
  LLM_MODELS,
  StreamingChunk,
  MessageReference,
} from '../../models/message.model';

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MarkdownModule,
    TextareaModule,
    ButtonModule,
    SelectModule,
    BadgeModule,
    ProgressSpinnerModule,
    ToastModule,
    TooltipModule,
  ],
  providers: [MessageService],
  templateUrl: './chat-interface.component.html',
  styleUrls: ['./chat-interface.component.scss'],
})
export class ChatInterfaceComponent implements OnInit, OnDestroy, AfterViewChecked {
  @Input() chatId!: string;
  @Input() workspaceId!: string;
  @Input() selectedPdfIds: string[] = [];

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  // Message data
  messages: Message[] = [];
  userInput: string = '';

  // LLM Model selection
  selectedModel: string = 'gpt-4o-mini';
  availableModels: LlmModel[] = LLM_MODELS;

  // State flags
  isLoading: boolean = false;
  isStreaming: boolean = false;
  isTyping: boolean = false;
  shouldAutoScroll: boolean = true;

  // Current streaming message
  currentStreamingMessage: Message | null = null;
  streamingContent: string = '';
  streamingReferences: MessageReference[] = [];

  // Subscriptions
  private subscriptions: Subscription[] = [];
  private scrollSubject = new Subject<void>();

  // Character count
  characterCount: number = 0;
  maxCharacters: number = 4000;

  constructor(
    private chatService: ChatService,
    private messageService: MessageService,
    private cdr: ChangeDetectorRef
  ) {
    // Debounce scroll operations
    this.subscriptions.push(
      this.scrollSubject.pipe(debounceTime(100)).subscribe(() => {
        this.scrollToBottom();
      })
    );
  }

  ngOnInit(): void {
    if (this.chatId) {
      this.loadMessages();
    }
  }

  ngAfterViewChecked(): void {
    if (this.shouldAutoScroll) {
      this.scrollSubject.next();
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((sub) => sub.unsubscribe());
  }

  /**
   * Load all messages for the current chat
   */
  loadMessages(): void {
    this.isLoading = true;

    this.subscriptions.push(
      this.chatService.getMessages(this.chatId).subscribe({
        next: (messages) => {
          this.messages = messages;
          this.isLoading = false;
          this.shouldAutoScroll = true;
        },
        error: (error) => {
          console.error('Error loading messages:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load messages',
          });
          this.isLoading = false;
        },
      })
    );
  }

  /**
   * Send a message
   */
  sendMessage(): void {
    if (!this.canSendMessage()) {
      return;
    }

    const userMessage = this.userInput.trim();
    this.userInput = '';
    this.characterCount = 0;

    // Add user message to UI immediately
    const newUserMessage: Message = {
      id: this.generateTempId(),
      chatHistoryId: this.chatId,
      content: userMessage,
      isUserMessage: true,
      timestamp: new Date(),
      references: [],
    };

    this.messages.push(newUserMessage);
    this.shouldAutoScroll = true;

    // Create placeholder for bot response
    this.currentStreamingMessage = {
      id: this.generateTempId(),
      chatHistoryId: this.chatId,
      content: '',
      isUserMessage: false,
      timestamp: new Date(),
      references: [],
      isStreaming: true,
    };

    this.messages.push(this.currentStreamingMessage);
    this.streamingContent = '';
    this.streamingReferences = [];
    this.isStreaming = true;
    this.isTyping = true;

    // Send message with streaming
    this.subscriptions.push(
      this.chatService
        .sendMessageWithFetch({
          query: userMessage,
          selectedPdfIds: this.selectedPdfIds,
          workspaceId: this.workspaceId,
          chatHistoryId: this.chatId,
          llmModel: this.selectedModel,
          chatHistory: this.buildChatHistory(),
        })
        .subscribe({
          next: (chunk) => this.handleStreamingChunk(chunk),
          error: (error) => this.handleStreamingError(error),
          complete: () => this.handleStreamingComplete(),
        })
    );
  }

  /**
   * Handle incoming streaming chunks
   */
  private handleStreamingChunk(chunk: StreamingChunk): void {
    this.isTyping = false;

    switch (chunk.type) {
      case 'token':
        if (chunk.content) {
          this.streamingContent += chunk.content;
          if (this.currentStreamingMessage) {
            this.currentStreamingMessage.content = this.streamingContent;
          }
          this.shouldAutoScroll = true;
          this.cdr.detectChanges();
        }
        break;

      case 'source':
        if (chunk.pdf && chunk.page !== undefined) {
          const reference: MessageReference = {
            pdf: chunk.pdf,
            page: chunk.page,
            pdfId: chunk.pdfId,
          };
          this.streamingReferences.push(reference);
          if (this.currentStreamingMessage) {
            this.currentStreamingMessage.references = [...this.streamingReferences];
          }
          this.cdr.detectChanges();
        }
        break;

      case 'done':
        if (chunk.answer && this.currentStreamingMessage) {
          this.currentStreamingMessage.content = chunk.answer;
        }
        if (chunk.references && this.currentStreamingMessage) {
          this.currentStreamingMessage.references = chunk.references;
        }
        break;

      case 'error':
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: chunk.message || 'An error occurred while processing your request',
        });
        break;
    }
  }

  /**
   * Handle streaming errors
   */
  private handleStreamingError(error: any): void {
    console.error('Streaming error:', error);
    this.isStreaming = false;
    this.isTyping = false;

    if (this.currentStreamingMessage) {
      this.currentStreamingMessage.content = '❌ Failed to get response. Please try again.';
      this.currentStreamingMessage.isStreaming = false;
    }

    this.messageService.add({
      severity: 'error',
      summary: 'Connection Error',
      detail: 'Failed to receive response from server',
      life: 5000,
    });
  }

  /**
   * Handle streaming completion
   */
  private handleStreamingComplete(): void {
    this.isStreaming = false;
    this.isTyping = false;

    if (this.currentStreamingMessage) {
      this.currentStreamingMessage.isStreaming = false;

      // Save bot message to database
      this.subscriptions.push(
        this.chatService
          .createMessage(this.chatId, {
            content: this.currentStreamingMessage.content,
            isUserMessage: false,
            references: this.currentStreamingMessage.references,
          })
          .subscribe({
            next: (savedMessage) => {
              // Update the temporary message with the saved one
              const index = this.messages.findIndex(
                (m) => m.id === this.currentStreamingMessage?.id
              );
              if (index !== -1) {
                this.messages[index] = savedMessage;
              }
            },
            error: (error) => {
              console.error('Error saving message:', error);
            },
          })
      );
    }

    this.currentStreamingMessage = null;
    this.streamingContent = '';
    this.streamingReferences = [];
  }

  /**
   * Retry sending a failed message
   */
  retryMessage(message: Message): void {
    // Remove the failed message
    const index = this.messages.findIndex((m) => m.id === message.id);
    if (index !== -1) {
      this.messages.splice(index, 1);
    }

    // Resend with the same content
    this.userInput = message.content;
    this.sendMessage();
  }

  /**
   * Handle Enter key press
   */
  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Update character count
   */
  onInputChange(): void {
    this.characterCount = this.userInput.length;
  }

  /**
   * Check if message can be sent
   */
  canSendMessage(): boolean {
    return (
      this.userInput.trim().length > 0 &&
      this.selectedPdfIds.length > 0 &&
      !this.isStreaming &&
      this.characterCount <= this.maxCharacters
    );
  }

  /**
   * Handle reference click
   */
  onReferenceClick(reference: MessageReference): void {
    // Emit event or navigate to PDF viewer with specific page
    console.log('Reference clicked:', reference);
    this.messageService.add({
      severity: 'info',
      summary: 'Reference',
      detail: `Opening ${reference.pdf}, Page ${reference.page}`,
    });
  }

  /**
   * Scroll to bottom of messages container
   */
  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        const element = this.messagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  /**
   * Build chat history for context
   */
  private buildChatHistory(): { role: string; content: string }[] {
    // Get last 5 messages for context
    const recentMessages = this.messages.slice(-10);

    return recentMessages
      .filter((m) => !m.isStreaming)
      .map((m) => ({
        role: m.isUserMessage ? 'user' : 'assistant',
        content: m.content,
      }));
  }

  /**
   * Generate temporary ID for optimistic UI updates
   */
  private generateTempId(): string {
    return `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Format timestamp for display
   */
  formatTimestamp(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return new Date(date).toLocaleDateString();
  }

  /**
   * Track by function for ngFor optimization
   */
  trackByMessageId(index: number, message: Message): string {
    return message.id;
  }
}
