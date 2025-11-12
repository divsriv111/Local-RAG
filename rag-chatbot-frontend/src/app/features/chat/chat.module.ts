import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { MarkdownModule } from 'ngx-markdown';
import { SharedModule } from '../../shared/shared.module';
import { ChatInterfaceComponent } from './components/chat-interface/chat-interface.component';

@NgModule({
  declarations: [],
  imports: [CommonModule, SharedModule, ChatInterfaceComponent, MarkdownModule.forChild()],
  providers: [provideHttpClient(withInterceptorsFromDi())],
  exports: [ChatInterfaceComponent],
})
export class ChatModule {}
