import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly THEME_KEY = 'app-theme';
  private themeSubject = new BehaviorSubject<Theme>(this.getStoredTheme());

  public theme$ = this.themeSubject.asObservable();

  constructor() {
    this.applyTheme(this.themeSubject.value);
  }

  private getStoredTheme(): Theme {
    const stored = localStorage.getItem(this.THEME_KEY);
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  }

  getCurrentTheme(): Theme {
    return this.themeSubject.value;
  }

  setTheme(theme: Theme): void {
    this.themeSubject.next(theme);
    localStorage.setItem(this.THEME_KEY, theme);
    this.applyTheme(theme);
  }

  toggleTheme(): void {
    const newTheme = this.themeSubject.value === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  private applyTheme(theme: Theme): void {
    document.documentElement.setAttribute('data-theme', theme);

    // Optionally switch PrimeNG theme
    const themeLink = document.getElementById('app-theme') as HTMLLinkElement;
    if (themeLink) {
      const themePath =
        theme === 'dark'
          ? 'node_modules/primeng/resources/themes/lara-dark-blue/theme.css'
          : 'node_modules/primeng/resources/themes/lara-light-blue/theme.css';
      themeLink.href = themePath;
    }
  }
}
