import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { ErrorComponent } from './shared/components/error/error.component';

export const routes: Routes = [
  // Root redirect - authenticated users go to workspaces, others to login
  {
    path: '',
    redirectTo: '/workspaces',
    pathMatch: 'full',
  },

  // Authentication routes (public)
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then((m) => m.AuthModule),
  },

  // Workspace routes (protected)
  {
    path: 'workspaces',
    loadChildren: () =>
      import('./features/workspace/workspace.module').then((m) => m.WorkspaceModule),
    canActivate: [authGuard],
  },

  // Workspace alias
  {
    path: 'workspace',
    redirectTo: 'workspaces',
    pathMatch: 'full',
  },

  // Chat routes (protected)
  {
    path: 'chat',
    loadChildren: () => import('./features/chat/chat.module').then((m) => m.ChatModule),
    canActivate: [authGuard],
  },

  // Profile route (protected)
  {
    path: 'profile',
    loadComponent: () =>
      import('./features/profile/profile.component').then((m) => m.ProfileComponent),
    canActivate: [authGuard],
  },

  // Error routes
  {
    path: 'error',
    component: ErrorComponent,
    children: [
      {
        path: '404',
        component: ErrorComponent,
        data: {
          errorCode: '404',
          errorTitle: 'Page Not Found',
          errorMessage: 'The page you are looking for does not exist.',
        },
      },
      {
        path: '403',
        component: ErrorComponent,
        data: {
          errorCode: '403',
          errorTitle: 'Access Denied',
          errorMessage: 'You do not have permission to access this resource.',
        },
      },
      {
        path: '500',
        component: ErrorComponent,
        data: {
          errorCode: '500',
          errorTitle: 'Server Error',
          errorMessage: 'An internal server error occurred. Please try again later.',
        },
      },
    ],
  },

  // Catch-all route for 404 errors
  {
    path: '**',
    component: ErrorComponent,
    data: {
      errorCode: '404',
      errorTitle: 'Page Not Found',
      errorMessage: 'The page you are looking for does not exist.',
    },
  },
];
