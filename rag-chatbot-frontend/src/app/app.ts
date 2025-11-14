import { Component, signal, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Menubar } from 'primeng/menubar';
import { Button } from 'primeng/button';
import { Drawer } from 'primeng/drawer';
import { Menu } from 'primeng/menu';
import { Toast } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { MenuItem } from 'primeng/api';
import { AuthService } from './core/services/auth.service';
import { ThemeService, Theme } from './core/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, Menubar, Button, Drawer, Menu, Toast],
  providers: [MessageService],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  protected readonly title = signal('RAG Chatbot');
  protected readonly currentYear = new Date().getFullYear();

  menuItems: MenuItem[] = [];
  userMenuItems: MenuItem[] = [];
  sidebarVisible = false;
  isAuthenticated = false;
  currentUser: any = null;
  currentTheme: Theme = 'light';

  constructor(
    private authService: AuthService,
    private router: Router,
    public messageService: MessageService,
    private themeService: ThemeService
  ) {}

  ngOnInit(): void {
    // Subscribe to authentication state
    this.authService.currentUser$.subscribe((user) => {
      this.currentUser = user;
      this.isAuthenticated = this.authService.isAuthenticated();
      this.buildMenuItems();
    });

    // Subscribe to theme changes
    this.themeService.theme$.subscribe((theme) => {
      this.currentTheme = theme;
    });
  }

  private buildMenuItems(): void {
    if (this.isAuthenticated) {
      this.menuItems = [
        {
          label: 'Workspaces',
          icon: 'pi pi-folder',
          command: () => this.navigateTo('/workspaces'),
        },
      ];

      this.userMenuItems = [
        {
          label: this.currentUser?.username || 'User',
          items: [
            {
              label: 'Profile',
              icon: 'pi pi-user',
              command: () => this.navigateTo('/profile'),
            },
            {
              separator: true,
            },
            {
              label: 'Logout',
              icon: 'pi pi-sign-out',
              command: () => this.logout(),
            },
          ],
        },
      ];
    } else {
      this.menuItems = [];
      this.userMenuItems = [];
    }
  }

  navigateTo(path: string): void {
    this.router.navigate([path]);
    this.sidebarVisible = false;
  }

  toggleSidebar(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }

  logout(): void {
    this.authService.logout();
    this.messageService.add({
      severity: 'success',
      summary: 'Logged Out',
      detail: 'You have been successfully logged out',
    });
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
    const newTheme = this.themeService.getCurrentTheme();
    this.messageService.add({
      severity: 'info',
      summary: 'Theme Changed',
      detail: `Switched to ${newTheme} mode`,
      life: 2000,
    });
  }

  get themeIcon(): string {
    return this.currentTheme === 'light' ? 'pi-moon' : 'pi-sun';
  }
}
