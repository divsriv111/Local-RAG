import { Component, OnInit, Input, Output, EventEmitter, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { MenuModule } from 'primeng/menu';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ToastModule } from 'primeng/toast';
import { ConfirmationService, MessageService, MenuItem } from 'primeng/api';
import { Subject } from 'rxjs';
import { takeUntil, finalize } from 'rxjs/operators';

import { ChatHistory } from '../../core/models/chat-history.model';
import { ChatHistoryService } from '../../core/services/chat-history.service';
import { RelativeTimePipe } from '../../shared/pipes/relative-time.pipe';

@Component({
  selector: 'app-chat-history-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    MenuModule,
    ConfirmDialogModule,
    ToastModule,
    RelativeTimePipe,
  ],
  providers: [ConfirmationService, MessageService],
  templateUrl: './chat-history-sidebar.component.html',
  styleUrls: ['./chat-history-sidebar.component.scss'],
})
export class ChatHistorySidebarComponent implements OnInit, OnDestroy {
  @Input() workspaceId!: string;
  @Input() activeChatId: string | null = null;
  @Output() chatSelected = new EventEmitter<ChatHistory>();
  @Output() newChatCreated = new EventEmitter<ChatHistory>();

  chatHistories: ChatHistory[] = [];
  filteredChatHistories: ChatHistory[] = [];
  showArchived = false;
  loading = false;
  sidebarVisible = false;
  isMobile = false;

  private destroy$ = new Subject<void>();

  constructor(
    private chatHistoryService: ChatHistoryService,
    private confirmationService: ConfirmationService,
    private messageService: MessageService
  ) {
    this.checkScreenSize();
  }

  ngOnInit(): void {
    if (!this.workspaceId) {
      console.error('WorkspaceId is required for ChatHistorySidebarComponent');
      return;
    }

    this.loadChatHistories();
    window.addEventListener('resize', this.checkScreenSize.bind(this));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    window.removeEventListener('resize', this.checkScreenSize.bind(this));
  }

  /**
   * Check screen size for responsive behavior
   */
  private checkScreenSize(): void {
    this.isMobile = window.innerWidth < 768;
  }

  /**
   * Load chat histories from the API
   */
  loadChatHistories(): void {
    this.loading = true;
    this.chatHistoryService
      .getAll(this.workspaceId, this.showArchived)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: (histories) => {
          this.chatHistories = histories;
          this.filterChatHistories();
        },
        error: (error) => {
          console.error('Error loading chat histories:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load chat histories',
          });
        },
      });
  }

  /**
   * Filter chat histories based on archive toggle
   */
  filterChatHistories(): void {
    this.filteredChatHistories = this.showArchived
      ? this.chatHistories
      : this.chatHistories.filter((chat) => !chat.isArchived);
  }

  /**
   * Toggle show archived chats
   */
  onShowArchivedChange(): void {
    this.filterChatHistories();
  }

  /**
   * Create a new chat
   */
  onNewChat(): void {
    this.loading = true;
    this.chatHistoryService
      .create(this.workspaceId)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: (newChat) => {
          this.chatHistories.unshift(newChat);
          this.filterChatHistories();
          this.newChatCreated.emit(newChat);
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'New chat created',
          });
        },
        error: (error) => {
          console.error('Error creating chat:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to create new chat',
          });
        },
      });
  }

  /**
   * Select a chat history
   */
  onChatSelect(chat: ChatHistory): void {
    this.activeChatId = chat.id;
    this.chatSelected.emit(chat);

    // Close sidebar on mobile after selection
    if (this.isMobile) {
      this.sidebarVisible = false;
    }
  }

  /**
   * Get context menu items for a chat
   */
  getMenuItems(chat: ChatHistory): MenuItem[] {
    return [
      {
        label: 'Rename',
        icon: 'pi pi-pencil',
        disabled: true, // Disabled for MVP
        command: () => this.onRenameChat(chat),
      },
      {
        label: chat.isArchived ? 'Unarchive' : 'Archive',
        icon: chat.isArchived ? 'pi pi-inbox' : 'pi pi-folder',
        command: () => this.onArchiveChat(chat),
      },
      {
        separator: true,
      },
      {
        label: 'Delete',
        icon: 'pi pi-trash',
        styleClass: 'text-danger',
        command: () => this.onDeleteChat(chat),
      },
    ];
  }

  /**
   * Show context menu
   */
  onContextMenu(event: MouseEvent, menu: any, chat: ChatHistory): void {
    event.preventDefault();
    menu.toggle(event);
  }

  /**
   * Rename chat (placeholder for MVP)
   */
  onRenameChat(chat: ChatHistory): void {
    // Placeholder for future implementation
    console.log('Rename chat:', chat.id);
  }

  /**
   * Archive/Unarchive chat
   */
  onArchiveChat(chat: ChatHistory): void {
    this.loading = true;
    this.chatHistoryService
      .archive(chat.id)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: () => {
          chat.isArchived = !chat.isArchived;
          this.filterChatHistories();
          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: chat.isArchived ? 'Chat archived' : 'Chat unarchived',
          });
        },
        error: (error) => {
          console.error('Error archiving chat:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to archive chat',
          });
        },
      });
  }

  /**
   * Delete chat with confirmation
   */
  onDeleteChat(chat: ChatHistory): void {
    this.confirmationService.confirm({
      message: `Are you sure you want to delete "${chat.name}"? This action cannot be undone.`,
      header: 'Delete Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        this.deleteChat(chat);
      },
    });
  }

  /**
   * Execute chat deletion
   */
  private deleteChat(chat: ChatHistory): void {
    this.loading = true;
    this.chatHistoryService
      .delete(chat.id)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => (this.loading = false))
      )
      .subscribe({
        next: () => {
          this.chatHistories = this.chatHistories.filter((c) => c.id !== chat.id);
          this.filterChatHistories();

          // Clear active chat if deleted
          if (this.activeChatId === chat.id) {
            this.activeChatId = null;
          }

          this.messageService.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Chat deleted successfully',
          });
        },
        error: (error) => {
          console.error('Error deleting chat:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete chat',
          });
        },
      });
  }

  /**
   * Toggle sidebar visibility (mobile)
   */
  toggleSidebar(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }

  /**
   * Track by function for ngFor
   */
  trackByChatId(index: number, chat: ChatHistory): string {
    return chat.id;
  }
}
