import { NgModule, Optional, SkipSelf } from '@angular/core';
import { CommonModule } from '@angular/common';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

// Services will be added here
// import { AuthService } from './services/auth.service';

// Guards will be added here
// import { AuthGuard } from './guards/auth.guard';

// Interceptors will be added here
// import { authInterceptor } from './interceptors/auth.interceptor';

@NgModule({
  declarations: [],
  imports: [
    CommonModule
  ],
  providers: [
    // Services
    // AuthService,
    
    // HTTP Client with interceptors
    provideHttpClient(
      // withInterceptors([authInterceptor])
    )
  ]
})
export class CoreModule {
  constructor(@Optional() @SkipSelf() parentModule: CoreModule) {
    if (parentModule) {
      throw new Error('CoreModule is already loaded. Import it in the AppModule only.');
    }
  }
}
