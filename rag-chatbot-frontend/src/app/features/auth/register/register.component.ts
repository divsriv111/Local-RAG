import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService, RegisterDTO } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body">
              <h2 class="card-title text-center mb-4">Register</h2>
              <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    formControlName="username"
                    [class.is-invalid]="
                      registerForm.get('username')?.invalid && registerForm.get('username')?.touched
                    "
                  />
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.get('username')?.errors?.['required']"
                  >
                    Username is required
                  </div>
                </div>
                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    formControlName="email"
                    [class.is-invalid]="
                      registerForm.get('email')?.invalid && registerForm.get('email')?.touched
                    "
                  />
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.get('email')?.errors?.['required']"
                  >
                    Email is required
                  </div>
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.get('email')?.errors?.['email']"
                  >
                    Invalid email format
                  </div>
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="password"
                    formControlName="password"
                    [class.is-invalid]="
                      registerForm.get('password')?.invalid && registerForm.get('password')?.touched
                    "
                  />
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.get('password')?.errors?.['required']"
                  >
                    Password is required
                  </div>
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.get('password')?.errors?.['minlength']"
                  >
                    Password must be at least 8 characters
                  </div>
                </div>
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input
                    type="password"
                    class="form-control"
                    id="confirmPassword"
                    formControlName="confirmPassword"
                    [class.is-invalid]="
                      registerForm.get('confirmPassword')?.invalid &&
                      registerForm.get('confirmPassword')?.touched
                    "
                  />
                  <div
                    class="invalid-feedback"
                    *ngIf="registerForm.errors?.['passwordMismatch'] && registerForm.get('confirmPassword')?.touched"
                  >
                    Passwords do not match
                  </div>
                </div>
                <div class="alert alert-danger" *ngIf="errorMessage">
                  {{ errorMessage }}
                </div>
                <div class="alert alert-success" *ngIf="successMessage">
                  {{ successMessage }}
                </div>
                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  [disabled]="registerForm.invalid || isLoading"
                >
                  <span *ngIf="isLoading">Registering...</span>
                  <span *ngIf="!isLoading">Register</span>
                </button>
              </form>
              <div class="text-center mt-3">
                <a routerLink="/auth/login">Already have an account? Login</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [],
})
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
    this.registerForm = this.fb.group(
      {
        username: ['', [Validators.required]],
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', [Validators.required]],
      },
      { validators: this.passwordMatchValidator }
    );
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');

    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';

      const { username, email, password } = this.registerForm.value;
      const registerData: RegisterDTO = { username, email, password };

      this.authService.register(registerData).subscribe({
        next: () => {
          this.isLoading = false;
          this.successMessage = 'Registration successful! Redirecting to login...';
          setTimeout(() => {
            this.router.navigate(['/auth/login']);
          }, 2000);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Registration failed. Please try again.';
        },
      });
    }
  }
}
