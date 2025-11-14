import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';

@Component({
  selector: 'app-error',
  standalone: true,
  imports: [CommonModule, ButtonModule, CardModule],
  templateUrl: './error.component.html',
  styleUrls: ['./error.component.scss'],
})
export class ErrorComponent implements OnInit {
  errorCode: string = '404';
  errorTitle: string = 'Page Not Found';
  errorMessage: string = 'The page you are looking for does not exist.';

  constructor(private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    // Get error details from route data or query params
    this.route.data.subscribe((data) => {
      if (data['errorCode']) {
        this.errorCode = data['errorCode'];
        this.errorTitle = data['errorTitle'] || this.getDefaultErrorTitle(data['errorCode']);
        this.errorMessage = data['errorMessage'] || this.getDefaultErrorMessage(data['errorCode']);
      }
    });

    this.route.queryParams.subscribe((params) => {
      if (params['code']) {
        this.errorCode = params['code'];
        this.errorTitle = params['title'] || this.getDefaultErrorTitle(params['code']);
        this.errorMessage = params['message'] || this.getDefaultErrorMessage(params['code']);
      }
    });
  }

  private getDefaultErrorTitle(code: string): string {
    const titles: { [key: string]: string } = {
      '400': 'Bad Request',
      '401': 'Unauthorized',
      '403': 'Forbidden',
      '404': 'Page Not Found',
      '500': 'Internal Server Error',
      '503': 'Service Unavailable',
    };
    return titles[code] || 'Error';
  }

  private getDefaultErrorMessage(code: string): string {
    const messages: { [key: string]: string } = {
      '400': 'The request could not be understood or was missing required parameters.',
      '401': 'You need to be authenticated to access this resource.',
      '403': 'You do not have permission to access this resource.',
      '404': 'The page you are looking for does not exist.',
      '500': 'An internal server error occurred. Please try again later.',
      '503': 'The service is temporarily unavailable. Please try again later.',
    };
    return messages[code] || 'An unexpected error occurred.';
  }

  goHome(): void {
    this.router.navigate(['/workspaces']);
  }

  goBack(): void {
    window.history.back();
  }
}
