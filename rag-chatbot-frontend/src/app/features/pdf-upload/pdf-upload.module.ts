import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

// PrimeNG Modules
import { PanelModule } from 'primeng/panel';
import { FileUploadModule } from 'primeng/fileupload';
import { ProgressBarModule } from 'primeng/progressbar';
import { CheckboxModule } from 'primeng/checkbox';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

// Component
import { PdfUploadComponent } from './pdf-upload.component';

@NgModule({
  declarations: [PdfUploadComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    PanelModule,
    FileUploadModule,
    ProgressBarModule,
    CheckboxModule,
    ButtonModule,
    TooltipModule,
    ToastModule,
  ],
  exports: [PdfUploadComponent],
  providers: [MessageService],
})
export class PdfUploadModule {}
