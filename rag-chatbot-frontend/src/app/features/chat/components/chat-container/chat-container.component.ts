import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ChatInterfaceComponent } from '../chat-interface/chat-interface.component';

/**
 * Example parent component showing how to integrate the ChatInterfaceComponent
 * This would typically be part of your workspace detail view
 */
@Component({
  selector: 'app-chat-container',
  standalone: true,
  imports: [CommonModule, ChatInterfaceComponent],
  template: `
    <div class="chat-container-wrapper">
      <div class="chat-header">
        <h2>{{ chatName || 'New Chat' }}</h2>
        <div class="chat-info">
          <span class="workspace-badge">
            <i class="pi pi-folder"></i>
            {{ workspaceName }}
          </span>
          <span class="pdf-count-badge">
            <i class="pi pi-file-pdf"></i>
            {{ selectedPdfIds.length }} PDFs selected
          </span>
        </div>
      </div>

      <!-- Chat Interface Component -->
      <app-chat-interface
        *ngIf="currentChatId && currentWorkspaceId"
        [chatId]="currentChatId"
        [workspaceId]="currentWorkspaceId"
        [selectedPdfIds]="selectedPdfIds"
      />

      <!-- Empty State when no chat selected -->
      <div *ngIf="!currentChatId" class="no-chat-selected">
        <i class="pi pi-comments" style="font-size: 4rem"></i>
        <h3>No chat selected</h3>
        <p>Create a new chat or select an existing one from the sidebar</p>
      </div>
    </div>
  `,
  styles: [
    `
      .chat-container-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .chat-header {
        padding: 1.5rem;
        border-bottom: 1px solid #dee2e6;
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
      }

      .chat-header h2 {
        margin: 0 0 0.75rem 0;
        color: #212529;
        font-size: 1.5rem;
        font-weight: 600;
      }

      .chat-info {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
      }

      .workspace-badge,
      .pdf-count-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.75rem;
        background: #e9ecef;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #495057;
      }

      .workspace-badge i,
      .pdf-count-badge i {
        font-size: 1rem;
        color: #007bff;
      }

      app-chat-interface {
        flex: 1;
        display: flex;
        overflow: hidden;
      }

      .no-chat-selected {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: var(--text-color-secondary);
        padding: 2rem;
        text-align: center;
      }

      .no-chat-selected h3 {
        margin: 1rem 0 0.5rem;
        color: var(--text-color);
      }

      .no-chat-selected p {
        margin: 0;
        max-width: 400px;
      }

      @media (max-width: 768px) {
        .chat-header {
          padding: 1rem;
        }

        .chat-header h2 {
          font-size: 1.25rem;
        }

        .chat-info {
          gap: 0.5rem;
        }

        .workspace-badge,
        .pdf-count-badge {
          font-size: 0.8rem;
          padding: 0.35rem 0.6rem;
        }
      }
    `,
  ],
})
export class ChatContainerComponent implements OnInit {
  // Chat state
  currentChatId: string = '';
  currentWorkspaceId: string = '';
  chatName: string = '';
  workspaceName: string = 'My Workspace';

  // Selected PDFs - this would typically come from a PDF selection component
  selectedPdfIds: string[] = [];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Get IDs from route parameters
    this.route.params.subscribe((params) => {
      this.currentWorkspaceId = params['workspaceId'] || '';
      this.currentChatId = params['chatId'] || '';
    });

    // Example: Load initial data
    this.loadWorkspaceData();
    this.loadChatData();
    this.loadSelectedPdfs();
  }

  /**
   * Load workspace data
   * Replace with actual API call
   */
  private loadWorkspaceData(): void {
    // TODO: Call workspace service
    // this.workspaceService.getById(this.currentWorkspaceId).subscribe(...)
    this.workspaceName = 'My Research Workspace';
  }

  /**
   * Load chat data
   * Replace with actual API call
   */
  private loadChatData(): void {
    if (this.currentChatId) {
      // TODO: Call chat service
      // this.chatService.getChatById(this.currentChatId).subscribe(...)
      this.chatName = 'Chat about AI Research';
    }
  }

  /**
   * Load selected PDFs
   * Replace with actual logic from PDF selection component
   */
  private loadSelectedPdfs(): void {
    // This would typically come from a PDF management service or state management
    // Example:
    this.selectedPdfIds = ['pdf-123-456', 'pdf-789-012', 'pdf-345-678'];
  }
}
