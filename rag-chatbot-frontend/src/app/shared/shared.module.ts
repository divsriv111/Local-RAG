import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

// PrimeNG imports will be added here as needed
// import { ButtonModule } from 'primeng/button';
// import { InputTextModule } from 'primeng/inputtext';
// import { CardModule } from 'primeng/card';

@NgModule({
  declarations: [
    // Shared components, pipes, and directives will be declared here
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    // PrimeNG modules
  ],
  exports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    // Export PrimeNG modules
    // Export shared components, pipes, and directives
  ],
})
export class SharedModule {}
