import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/auth/login',
    pathMatch: 'full'
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then(m => m.AuthModule)
  },
  {
    path: 'workspaces',
    loadChildren: () => import('./features/workspace/workspace.module').then(m => m.WorkspaceModule),
    canActivate: [authGuard]
  },
  {
    path: 'chat',
    loadChildren: () => import('./features/chat/chat.module').then(m => m.ChatModule),
    canActivate: [authGuard]
  },
  {
    path: '**',
    redirectTo: '/auth/login'
  }
];
