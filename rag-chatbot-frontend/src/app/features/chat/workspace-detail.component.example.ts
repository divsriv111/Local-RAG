import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ChatHistorySidebarComponent } from './chat-history-sidebar.component';
import { ChatHistory } from '../../core/models/chat-history.model';

/**
 * Example Workspace Detail Component
 * Demonstrates how to integrate the ChatHistorySidebarComponent
 * with a complete workspace layout including chat interface and PDF upload
 */
@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [
    CommonModule,
    ChatHistorySidebarComponent,
    // Add your ChatInterfaceComponent here
    // Add your PdfUploadComponent here
  ],
  templateUrl: './workspace-detail.component.html',
  styleUrls: ['./workspace-detail.component.scss'],
})
export class WorkspaceDetailComponent implements OnInit {
  workspaceId!: string;
  activeChatId: string | null = null;
  selectedChatName = 'New Chat';

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Get workspace ID from route parameters
    this.route.paramMap.subscribe((params) => {
      const id = params.get('id');
      if (id) {
        this.workspaceId = id;
      }
    });
  }

  /**
   * Handle chat selection from sidebar
   * @param chat - The selected chat history
   */
  onChatSelected(chat: ChatHistory): void {
    console.log('Chat selected:', chat);
    this.activeChatId = chat.id;
    this.selectedChatName = chat.name;

    // TODO: Load messages for this chat
    // this.messageService.getMessages(chat.id).subscribe(messages => {
    //   this.messages = messages;
    // });
  }

  /**
   * Handle new chat creation from sidebar
   * @param chat - The newly created chat
   */
  onNewChatCreated(chat: ChatHistory): void {
    console.log('New chat created:', chat);
    this.activeChatId = chat.id;
    this.selectedChatName = chat.name;

    // TODO: Initialize empty chat interface
    // this.messages = [];
  }

  /**
   * Handle PDF selection changes
   * @param pdfIds - Array of selected PDF IDs
   */
  onPdfSelectionChanged(pdfIds: string[]): void {
    console.log('PDF selection changed:', pdfIds);
    // Update the selected PDFs for RAG queries
  }

  /**
   * Handle new message sent from chat interface
   * @param message - The message content
   */
  onMessageSent(message: string): void {
    console.log('Message sent:', message);
    // TODO: Send to LLM service and handle response
  }
}
