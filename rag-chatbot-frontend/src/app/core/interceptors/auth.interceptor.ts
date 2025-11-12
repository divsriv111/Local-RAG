import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.getToken();

  // Clone request and add authorization header if token exists
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Unauthorized - token expired or invalid, redirect to login
        authService.logout();
        router.navigate(['/auth/login'], {
          queryParams: { message: 'Session expired. Please login again.' },
        });
      } else if (error.status === 403) {
        // Forbidden - user doesn't have permission
        console.error('Access forbidden:', error.message);
        // You can show a toast notification here if needed
        // For now, just log and pass the error through
      }
      return throwError(() => error);
    })
  );
};
