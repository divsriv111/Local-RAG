import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body">
              <h2 class="card-title text-center mb-4">Login</h2>
              <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="username" 
                    formControlName="username"
                    [class.is-invalid]="loginForm.get('username')?.invalid && loginForm.get('username')?.touched">
                  <div class="invalid-feedback" *ngIf="loginForm.get('username')?.errors?.['required']">
                    Username is required
                  </div>
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    formControlName="password"
                    [class.is-invalid]="loginForm.get('password')?.invalid && loginForm.get('password')?.touched">
                  <div class="invalid-feedback" *ngIf="loginForm.get('password')?.errors?.['required']">
                    Password is required
                  </div>
                </div>
                <div class="alert alert-danger" *ngIf="errorMessage">
                  {{ errorMessage }}
                </div>
                <button type="submit" class="btn btn-primary w-100" [disabled]="loginForm.invalid || isLoading">
                  <span *ngIf="isLoading">Logging in...</span>
                  <span *ngIf="!isLoading">Login</span>
                </button>
              </form>
              <div class="text-center mt-3">
                <a routerLink="/auth/register">Don't have an account? Register</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      
      const { username, password } = this.loginForm.value;
      
      this.authService.login(username, password).subscribe({
        next: () => {
          this.router.navigate(['/workspaces']);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Login failed. Please try again.';
        }
      });
    }
  }
}
