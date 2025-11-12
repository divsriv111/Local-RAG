import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { WorkspaceService } from '../../../core/services/workspace.service';
import { Workspace } from '../../../core/models/workspace.models';
import { MessageService } from 'primeng/api';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TooltipModule } from 'primeng/tooltip';
import { ToastModule } from 'primeng/toast';
import { CreateWorkspaceDialogComponent } from '../create-workspace-dialog/create-workspace-dialog.component';

@Component({
  selector: 'app-workspace-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    ProgressSpinnerModule,
    TooltipModule,
    ToastModule,
    CreateWorkspaceDialogComponent,
  ],
  providers: [MessageService],
  templateUrl: './workspace-list.component.html',
  styleUrls: ['./workspace-list.component.scss'],
})
export class WorkspaceListComponent implements OnInit, OnDestroy {
  workspaces: Workspace[] = [];
  filteredWorkspaces: Workspace[] = [];
  searchTerm = '';
  loading = false;
  displayCreateDialog = false;

  private destroy$ = new Subject<void>();
  private searchSubject$ = new Subject<string>();

  constructor(
    private workspaceService: WorkspaceService,
    private router: Router,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.loadWorkspaces();
    this.setupSearch();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load all workspaces from the server
   */
  loadWorkspaces(): void {
    this.loading = true;
    this.workspaceService
      .getAll()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (workspaces) => {
          this.workspaces = workspaces;
          this.filteredWorkspaces = workspaces;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading workspaces:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load workspaces',
          });
          this.loading = false;
        },
      });
  }

  /**
   * Setup real-time search with debouncing
   */
  private setupSearch(): void {
    this.searchSubject$
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe((searchTerm) => {
        this.filterWorkspaces(searchTerm);
      });
  }

  /**
   * Handle search input change
   */
  onSearchChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.searchSubject$.next(input.value);
  }

  /**
   * Filter workspaces by search term (case-insensitive)
   */
  private filterWorkspaces(searchTerm: string): void {
    if (!searchTerm.trim()) {
      this.filteredWorkspaces = this.workspaces;
      return;
    }

    const term = searchTerm.toLowerCase();
    this.filteredWorkspaces = this.workspaces.filter((workspace) =>
      workspace.name.toLowerCase().includes(term)
    );
  }

  /**
   * Navigate to workspace detail page
   */
  onWorkspaceClick(workspace: Workspace): void {
    this.router.navigate(['/workspaces', workspace.id]);
  }

  /**
   * Show create workspace dialog
   */
  showCreateDialog(): void {
    this.displayCreateDialog = true;
  }

  /**
   * Handle workspace creation
   */
  onWorkspaceCreated(): void {
    this.displayCreateDialog = false;
    this.loadWorkspaces();
  }

  /**
   * Handle dialog close
   */
  onDialogClose(): void {
    this.displayCreateDialog = false;
  }

  /**
   * Format date for display
   */
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }
}
