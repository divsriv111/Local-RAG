/**
 * PDF Upload Component - Complete Usage Example
 *
 * This file demonstrates how to integrate the PDF Upload Component
 * into your Angular application with various use cases.
 */

import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PdfUploadComponent } from './pdf-upload.component';
import { PdfService } from '../../core/services/pdf.service';
import { PdfDocument } from '../../core/models/pdf-document.model';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

/**
 * Example 1: Basic Integration
 * Simple workspace with PDF upload functionality
 */
@Component({
  selector: 'app-basic-example',
  standalone: true,
  imports: [CommonModule, PdfUploadComponent, ToastModule],
  providers: [MessageService],
  template: `
    <div class="container-fluid p-4">
      <div class="row">
        <!-- PDF Upload Sidebar -->
        <div class="col-lg-3 col-md-4 mb-3">
          <app-pdf-upload
            [workspaceId]="workspaceId"
            (selectedPdfsChange)="handlePdfSelection($event)"
            (pdfListChange)="handlePdfListUpdate($event)"
          ></app-pdf-upload>
        </div>

        <!-- Main Content Area -->
        <div class="col-lg-9 col-md-8">
          <div class="card">
            <div class="card-body">
              <h5>Selected PDFs</h5>
              <p *ngIf="selectedPdfIds.length === 0" class="text-muted">
                No PDFs selected. Please select PDFs from the sidebar.
              </p>
              <ul *ngIf="selectedPdfIds.length > 0">
                <li *ngFor="let id of selectedPdfIds">{{ id }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p-toast position="top-right"></p-toast>
  `,
})
export class BasicExampleComponent implements OnInit {
  workspaceId = 'workspace-123';
  selectedPdfIds: string[] = [];
  pdfList: PdfDocument[] = [];

  constructor(private messageService: MessageService) {}

  ngOnInit(): void {
    console.log('Workspace initialized:', this.workspaceId);
  }

  handlePdfSelection(selectedIds: string[]): void {
    this.selectedPdfIds = selectedIds;
    console.log('PDF selection changed:', selectedIds);

    if (selectedIds.length > 0) {
      this.messageService.add({
        severity: 'info',
        summary: 'Selection Updated',
        detail: `${selectedIds.length} PDF(s) selected`,
      });
    }
  }

  handlePdfListUpdate(pdfs: PdfDocument[]): void {
    this.pdfList = pdfs;
    console.log('PDF list updated:', pdfs);
  }
}

/**
 * Example 2: Advanced Integration with Chat
 * Shows PDF upload integrated with a chat interface
 */
@Component({
  selector: 'app-chat-example',
  standalone: true,
  imports: [CommonModule, PdfUploadComponent, ToastModule],
  providers: [MessageService],
  template: `
    <div class="workspace-container">
      <!-- Left Sidebar: Chat History -->
      <div class="sidebar-left">
        <div class="chat-history-panel">
          <h6>Chat History</h6>
          <!-- Chat history list here -->
        </div>
      </div>

      <!-- Center: Chat Interface -->
      <div class="chat-main">
        <div class="chat-header">
          <h5>Chat: {{ currentChatName }}</h5>
          <span class="badge bg-info" *ngIf="hasSelectedPdfs()">
            {{ selectedPdfIds.length }} PDF(s) selected
          </span>
          <span class="badge bg-warning" *ngIf="!hasSelectedPdfs()"> No PDFs selected </span>
        </div>

        <div class="chat-messages">
          <!-- Messages display here -->
        </div>

        <div class="chat-input">
          <textarea
            placeholder="Type your message..."
            [disabled]="!hasSelectedPdfs()"
            class="form-control"
          ></textarea>
          <button
            class="btn btn-primary mt-2"
            [disabled]="!hasSelectedPdfs()"
            (click)="sendMessage()"
          >
            Send
          </button>
          <p *ngIf="!hasSelectedPdfs()" class="text-warning mt-2">
            <i class="pi pi-exclamation-triangle"></i>
            Please select at least one PDF to start chatting
          </p>
        </div>
      </div>

      <!-- Right Sidebar: PDF Upload -->
      <div class="sidebar-right">
        <app-pdf-upload
          [workspaceId]="workspaceId"
          (selectedPdfsChange)="onPdfSelectionChange($event)"
        ></app-pdf-upload>
      </div>
    </div>
    <p-toast></p-toast>
  `,
  styles: [
    `
      .workspace-container {
        display: flex;
        height: 100vh;
      }

      .sidebar-left {
        width: 250px;
        border-right: 1px solid #dee2e6;
        overflow-y: auto;
      }

      .chat-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 1rem;
      }

      .sidebar-right {
        width: 300px;
        border-left: 1px solid #dee2e6;
        overflow-y: auto;
      }

      .chat-messages {
        flex: 1;
        overflow-y: auto;
        margin: 1rem 0;
      }

      @media (max-width: 992px) {
        .workspace-container {
          flex-direction: column;
        }

        .sidebar-left,
        .sidebar-right {
          width: 100%;
          border: none;
          border-bottom: 1px solid #dee2e6;
        }
      }
    `,
  ],
})
export class ChatExampleComponent {
  workspaceId = 'workspace-456';
  currentChatName = 'New Chat';
  selectedPdfIds: string[] = [];

  onPdfSelectionChange(selectedIds: string[]): void {
    this.selectedPdfIds = selectedIds;
  }

  hasSelectedPdfs(): boolean {
    return this.selectedPdfIds.length > 0;
  }

  sendMessage(): void {
    if (!this.hasSelectedPdfs()) {
      return;
    }

    // Send message with selected PDF context
    console.log('Sending message with PDFs:', this.selectedPdfIds);
  }
}

/**
 * Example 3: Programmatic Control
 * Demonstrates how to control the component programmatically
 */
@Component({
  selector: 'app-programmatic-example',
  standalone: true,
  imports: [CommonModule, PdfUploadComponent, ToastModule],
  template: `
    <div class="container p-4">
      <div class="row mb-3">
        <div class="col">
          <h4>Programmatic Control Example</h4>
          <div class="btn-group">
            <button class="btn btn-primary" (click)="selectAllPdfs()">Select All</button>
            <button class="btn btn-secondary" (click)="clearSelection()">Clear Selection</button>
            <button class="btn btn-info" (click)="getSelectedInfo()">Show Selected</button>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-4">
          <app-pdf-upload
            #pdfUpload
            [workspaceId]="workspaceId"
            (selectedPdfsChange)="onSelectionChange($event)"
            (pdfListChange)="onListChange($event)"
          ></app-pdf-upload>
        </div>

        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h6>Component State</h6>
            </div>
            <div class="card-body">
              <p><strong>Total PDFs:</strong> {{ totalPdfs }}</p>
              <p><strong>Selected PDFs:</strong> {{ selectedCount }}</p>
              <div *ngIf="selectedPdfs.length > 0">
                <h6>Selected Files:</h6>
                <ul>
                  <li *ngFor="let pdf of selectedPdfs">
                    {{ pdf.fileName }} ({{ formatSize(pdf.fileSize) }})
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p-toast></p-toast>
  `,
})
export class ProgrammaticExampleComponent {
  @ViewChild('pdfUpload') pdfUploadComponent!: PdfUploadComponent;

  workspaceId = 'workspace-789';
  allPdfs: PdfDocument[] = [];
  selectedPdfs: PdfDocument[] = [];
  totalPdfs = 0;
  selectedCount = 0;

  constructor(private pdfService: PdfService, private messageService: MessageService) {}

  onSelectionChange(selectedIds: string[]): void {
    this.selectedCount = selectedIds.length;
    this.selectedPdfs = this.allPdfs.filter((pdf) => selectedIds.includes(pdf.id));
  }

  onListChange(pdfs: PdfDocument[]): void {
    this.allPdfs = pdfs;
    this.totalPdfs = pdfs.length;
  }

  selectAllPdfs(): void {
    if (this.allPdfs.length === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'No PDFs',
        detail: 'Please upload PDFs first',
      });
      return;
    }

    const allIds = this.allPdfs.map((pdf) => pdf.id);
    this.pdfService.updateSelection(allIds);

    this.messageService.add({
      severity: 'success',
      summary: 'All Selected',
      detail: `Selected all ${allIds.length} PDFs`,
    });
  }

  clearSelection(): void {
    this.pdfService.clearSelection();

    this.messageService.add({
      severity: 'info',
      summary: 'Selection Cleared',
      detail: 'All selections have been cleared',
    });
  }

  getSelectedInfo(): void {
    const selected = this.pdfService.getSelectedPdfIds();

    this.messageService.add({
      severity: 'info',
      summary: 'Selected PDFs',
      detail: `${selected.size} PDF(s) currently selected`,
      life: 5000,
    });

    console.log('Selected PDF IDs:', Array.from(selected));
  }

  formatSize(bytes: number): string {
    return this.pdfUploadComponent?.formatFileSize(bytes) || '0 Bytes';
  }
}

/**
 * Example 4: Multi-Workspace Support
 * Shows how to handle multiple workspaces
 */
@Component({
  selector: 'app-multi-workspace-example',
  standalone: true,
  imports: [CommonModule, FormsModule, PdfUploadComponent, ToastModule],
  template: `
    <div class="container-fluid p-4">
      <div class="row mb-3">
        <div class="col">
          <h4>Multi-Workspace Example</h4>
          <select
            class="form-select"
            [(ngModel)]="activeWorkspaceId"
            (change)="onWorkspaceChange()"
          >
            <option *ngFor="let workspace of workspaces" [value]="workspace.id">
              {{ workspace.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="row">
        <div class="col-lg-4">
          <app-pdf-upload
            [workspaceId]="activeWorkspaceId"
            (selectedPdfsChange)="handleSelection($event)"
            (pdfListChange)="handleListUpdate($event)"
          ></app-pdf-upload>
        </div>

        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h6>Current Workspace: {{ getWorkspaceName(activeWorkspaceId) }}</h6>
            </div>
            <div class="card-body">
              <p>PDFs in this workspace: {{ currentWorkspacePdfs.length }}</p>
              <p>Selected PDFs: {{ currentSelection.length }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p-toast></p-toast>
  `,
})
export class MultiWorkspaceExampleComponent implements OnInit {
  workspaces = [
    { id: 'ws-1', name: 'Project Alpha' },
    { id: 'ws-2', name: 'Project Beta' },
    { id: 'ws-3', name: 'Research Papers' },
  ];

  activeWorkspaceId = 'ws-1';
  currentWorkspacePdfs: PdfDocument[] = [];
  currentSelection: string[] = [];

  constructor(private pdfService: PdfService, private messageService: MessageService) {}

  ngOnInit(): void {
    this.onWorkspaceChange();
  }

  onWorkspaceChange(): void {
    // Clear previous selection when switching workspaces
    this.pdfService.clearSelection();

    this.messageService.add({
      severity: 'info',
      summary: 'Workspace Changed',
      detail: `Switched to ${this.getWorkspaceName(this.activeWorkspaceId)}`,
    });
  }

  handleSelection(selectedIds: string[]): void {
    this.currentSelection = selectedIds;
  }

  handleListUpdate(pdfs: PdfDocument[]): void {
    this.currentWorkspacePdfs = pdfs;
  }

  getWorkspaceName(id: string): string {
    return this.workspaces.find((ws) => ws.id === id)?.name || 'Unknown';
  }
}
