import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { WorkspaceService } from '../../../core/services/workspace.service';
import { Workspace } from '../../../core/models/workspace.models';
import { MessageService } from 'primeng/api';

// PrimeNG Imports
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SplitterModule } from 'primeng/splitter';
import { PanelModule } from 'primeng/panel';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    TooltipModule,
    ProgressSpinnerModule,
    SplitterModule,
    PanelModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './workspace-detail.component.html',
  styleUrls: ['./workspace-detail.component.scss'],
})
export class WorkspaceDetailComponent implements OnInit, OnDestroy {
  workspace: Workspace | null = null;
  workspaceId: string | null = null;
  loading = false;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private workspaceService: WorkspaceService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe((params) => {
      this.workspaceId = params['id'];
      if (this.workspaceId) {
        this.loadWorkspace(this.workspaceId);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load workspace details
   */
  private loadWorkspace(id: string): void {
    this.loading = true;
    this.workspaceService
      .getById(id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (workspace) => {
          this.workspace = workspace;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading workspace:', error);
          this.messageService.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load workspace',
          });
          this.loading = false;
          // Navigate back to workspace list if workspace not found
          if (error.status === 404) {
            this.router.navigate(['/workspaces']);
          }
        },
      });
  }

  /**
   * Navigate back to workspace list
   */
  goBack(): void {
    this.router.navigate(['/workspaces']);
  }
}
