import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, UpdateUserDTO } from '../models/user.model';

@Injectable({
  providedIn: 'root',
})
export class ProfileService {
  private apiUrl = `${environment.apiUrl}/api/users`;

  constructor(private http: HttpClient) {}

  /**
   * Get the current user's profile information
   */
  getProfile(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/profile`);
  }

  /**
   * Update the current user's profile information
   * @param user - Updated user data (username, email)
   */
  updateProfile(user: UpdateUserDTO): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/profile`, user);
  }

  /**
   * Change the current user's password
   * @param currentPassword - Current password for verification
   * @param newPassword - New password to set
   */
  changePassword(currentPassword: string, newPassword: string): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/change-password`, {
      currentPassword,
      newPassword,
    });
  }
}
