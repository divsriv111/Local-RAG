import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
  ValidationErrors,
} from '@angular/forms';
import { MessageService } from 'primeng/api';
import { ProfileService } from '../../core/services/profile.service';
import { User, UpdateUserDTO } from '../../core/models/user.model';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
  standalone: false,
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;
  passwordForm!: FormGroup;
  currentUser: User | null = null;
  isLoadingProfile = false;
  isUpdatingProfile = false;
  isChangingPassword = false;
  passwordPanelCollapsed: boolean = true;

  constructor(
    private fb: FormBuilder,
    private profileService: ProfileService,
    private messageService: MessageService
  ) {}

  /**
   * Handle panel collapse change event
   */
  onPanelCollapseChange(collapsed: boolean | undefined): void {
    this.passwordPanelCollapsed = collapsed ?? true;
  }

  ngOnInit(): void {
    this.initializeForms();
    this.loadProfile();
  }

  /**
   * Initialize reactive forms with validation
   */
  private initializeForms(): void {
    // Profile form
    this.profileForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
    });

    // Password form with custom validators
    this.passwordForm = this.fb.group(
      {
        currentPassword: ['', Validators.required],
        newPassword: ['', [Validators.required, this.passwordStrengthValidator]],
        confirmPassword: ['', Validators.required],
      },
      { validators: this.passwordMatchValidator }
    );
  }

  /**
   * Password strength validator
   * Requires: min 8 chars, 1 uppercase, 1 number, 1 special char
   */
  private passwordStrengthValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) {
      return null;
    }

    const hasMinLength = value.length >= 8;
    const hasUpperCase = /[A-Z]/.test(value);
    const hasNumber = /[0-9]/.test(value);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value);

    const passwordValid = hasMinLength && hasUpperCase && hasNumber && hasSpecialChar;

    if (!passwordValid) {
      return {
        passwordStrength: {
          hasMinLength,
          hasUpperCase,
          hasNumber,
          hasSpecialChar,
        },
      };
    }

    return null;
  }

  /**
   * Validator to check if password and confirm password match
   */
  private passwordMatchValidator(group: AbstractControl): ValidationErrors | null {
    const newPassword = group.get('newPassword')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;

    if (newPassword && confirmPassword && newPassword !== confirmPassword) {
      return { passwordMismatch: true };
    }

    return null;
  }

  /**
   * Load current user profile
   */
  loadProfile(): void {
    this.isLoadingProfile = true;
    this.profileService.getProfile().subscribe({
      next: (user) => {
        this.currentUser = user;
        this.profileForm.patchValue({
          username: user.username,
          email: user.email,
        });
        this.isLoadingProfile = false;
      },
      error: (error) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load profile information',
        });
        this.isLoadingProfile = false;
      },
    });
  }

  /**
   * Update user profile
   */
  updateProfile(): void {
    if (this.profileForm.invalid) {
      this.markFormGroupTouched(this.profileForm);
      return;
    }

    this.isUpdatingProfile = true;
    const updateData: UpdateUserDTO = this.profileForm.value;

    this.profileService.updateProfile(updateData).subscribe({
      next: (user) => {
        this.currentUser = user;
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Profile updated successfully',
        });
        this.isUpdatingProfile = false;
      },
      error: (error) => {
        const errorMessage =
          error.status === 400
            ? 'Invalid profile data. Please check your input.'
            : 'Failed to update profile. Please try again.';

        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
        });
        this.isUpdatingProfile = false;
      },
    });
  }

  /**
   * Cancel profile changes and revert to original values
   */
  cancelProfileChanges(): void {
    if (this.currentUser) {
      this.profileForm.patchValue({
        username: this.currentUser.username,
        email: this.currentUser.email,
      });
      this.profileForm.markAsPristine();
      this.profileForm.markAsUntouched();
    }
  }

  /**
   * Change user password
   */
  changePassword(): void {
    if (this.passwordForm.invalid) {
      this.markFormGroupTouched(this.passwordForm);
      return;
    }

    this.isChangingPassword = true;
    const { currentPassword, newPassword } = this.passwordForm.value;

    this.profileService.changePassword(currentPassword, newPassword).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Password changed successfully',
        });
        this.passwordForm.reset();
        this.passwordPanelCollapsed = true;
        this.isChangingPassword = false;
      },
      error: (error) => {
        let errorMessage = 'Failed to change password. Please try again.';

        if (error.status === 401) {
          errorMessage = 'Current password is incorrect';
        } else if (error.status === 400) {
          errorMessage = 'Invalid password. Please check the requirements.';
        }

        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
        });
        this.isChangingPassword = false;
      },
    });
  }

  /**
   * Cancel password change and reset form
   */
  cancelPasswordChange(): void {
    this.passwordForm.reset();
    this.passwordPanelCollapsed = true;
  }

  /**
   * Mark all fields in a form group as touched to show validation errors
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
   * Get error message for a form control
   */
  getErrorMessage(formGroup: FormGroup, fieldName: string): string {
    const control = formGroup.get(fieldName);

    if (!control || !control.touched || !control.errors) {
      return '';
    }

    const errors = control.errors;

    if (errors['required']) {
      return `${this.getFieldLabel(fieldName)} is required`;
    }
    if (errors['email']) {
      return 'Please enter a valid email address';
    }
    if (errors['minlength']) {
      return `${this.getFieldLabel(fieldName)} must be at least ${
        errors['minlength'].requiredLength
      } characters`;
    }
    if (errors['maxlength']) {
      return `${this.getFieldLabel(fieldName)} must not exceed ${
        errors['maxlength'].requiredLength
      } characters`;
    }
    if (errors['passwordStrength']) {
      const strength = errors['passwordStrength'];
      const missing = [];
      if (!strength.hasMinLength) missing.push('at least 8 characters');
      if (!strength.hasUpperCase) missing.push('one uppercase letter');
      if (!strength.hasNumber) missing.push('one number');
      if (!strength.hasSpecialChar) missing.push('one special character');
      return `Password must contain ${missing.join(', ')}`;
    }

    return 'Invalid input';
  }

  /**
   * Get form-level error message (e.g., password mismatch)
   */
  getFormError(formGroup: FormGroup): string {
    if (formGroup.errors?.['passwordMismatch'] && formGroup.get('confirmPassword')?.touched) {
      return 'Passwords do not match';
    }
    return '';
  }

  /**
   * Get user-friendly field label
   */
  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      username: 'Username',
      email: 'Email',
      currentPassword: 'Current password',
      newPassword: 'New password',
      confirmPassword: 'Confirm password',
    };
    return labels[fieldName] || fieldName;
  }

  /**
   * Check if a field has an error
   */
  hasError(formGroup: FormGroup, fieldName: string): boolean {
    const control = formGroup.get(fieldName);
    return !!(control && control.invalid && control.touched);
  }
}
