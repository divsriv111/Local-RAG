import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { WorkspaceService } from '../../../core/services/workspace.service';
import { MessageService } from 'primeng/api';

// PrimeNG Imports
import { DialogModule } from 'primeng/dialog';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-create-workspace-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, DialogModule, ButtonModule, InputTextModule],
  templateUrl: './create-workspace-dialog.component.html',
  styleUrls: ['./create-workspace-dialog.component.scss'],
})
export class CreateWorkspaceDialogComponent {
  @Input() visible = false;
  @Output() visibleChange = new EventEmitter<boolean>();
  @Output() workspaceCreated = new EventEmitter<void>();
  @Output() dialogClosed = new EventEmitter<void>();

  workspaceForm: FormGroup;
  submitting = false;

  constructor(
    private fb: FormBuilder,
    private workspaceService: WorkspaceService,
    private messageService: MessageService
  ) {
    this.workspaceForm = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(100)]],
    });
  }

  /**
   * Handle dialog hide event
   */
  onHide(): void {
    this.workspaceForm.reset();
    this.visible = false;
    this.visibleChange.emit(false);
    this.dialogClosed.emit();
  }

  /**
   * Handle form submission
   */
  onSubmit(): void {
    if (this.workspaceForm.invalid) {
      this.markFormGroupTouched(this.workspaceForm);
      return;
    }

    this.submitting = true;
    const name = this.workspaceForm.get('name')?.value;

    this.workspaceService.create(name).subscribe({
      next: (workspace) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: `Workspace "${workspace.name}" created successfully`,
        });
        this.submitting = false;
        this.workspaceForm.reset();
        this.workspaceCreated.emit();
        this.onHide();
      },
      error: (error) => {
        console.error('Error creating workspace:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: error.error?.message || 'Failed to create workspace',
        });
        this.submitting = false;
      },
    });
  }

  /**
   * Handle cancel button click
   */
  onCancel(): void {
    this.onHide();
  }

  /**
   * Mark all form fields as touched to show validation errors
   */
  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach((key) => {
      const control = formGroup.get(key);
      control?.markAsTouched();

      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  /**
   * Check if form field has error
   */
  hasError(fieldName: string, errorType: string): boolean {
    const field = this.workspaceForm.get(fieldName);
    return !!(field && field.hasError(errorType) && (field.dirty || field.touched));
  }

  /**
   * Get error message for field
   */
  getErrorMessage(fieldName: string): string {
    const field = this.workspaceForm.get(fieldName);
    if (!field || !field.errors || (!field.dirty && !field.touched)) {
      return '';
    }

    if (field.hasError('required')) {
      return 'Workspace name is required';
    }

    if (field.hasError('maxlength')) {
      return 'Workspace name must not exceed 100 characters';
    }

    return '';
  }
}
