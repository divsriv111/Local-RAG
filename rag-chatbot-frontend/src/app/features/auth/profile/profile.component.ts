import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container mt-5">
      <h2>Profile</h2>
      <p>Profile component - To be implemented</p>
    </div>
  `,
  styles: []
})
export class ProfileComponent {
}
