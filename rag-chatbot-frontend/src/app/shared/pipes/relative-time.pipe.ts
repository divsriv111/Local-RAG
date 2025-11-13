import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'relativeTime',
  standalone: true,
})
export class RelativeTimePipe implements PipeTransform {
  transform(value: Date | string | null | undefined): string {
    if (!value) {
      return '';
    }

    const date = value instanceof Date ? value : new Date(value);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 0) {
      return 'Just now';
    }

    const intervals: { [key: string]: number } = {
      year: 31536000,
      month: 2592000,
      week: 604800,
      day: 86400,
      hour: 3600,
      minute: 60,
      second: 1,
    };

    for (const [name, secondsInInterval] of Object.entries(intervals)) {
      const interval = Math.floor(seconds / secondsInInterval);

      if (interval >= 1) {
        if (name === 'second' && interval < 10) {
          return 'Just now';
        }

        if (name === 'minute' && interval === 1) {
          return '1 min ago';
        }

        if (name === 'minute' && interval < 60) {
          return `${interval} mins ago`;
        }

        if (name === 'hour' && interval === 1) {
          return '1 hour ago';
        }

        if (name === 'hour' && interval < 24) {
          return `${interval} hours ago`;
        }

        if (name === 'day' && interval === 1) {
          return '1 day ago';
        }

        if (name === 'day' && interval < 7) {
          return `${interval} days ago`;
        }

        if (name === 'week' && interval === 1) {
          return '1 week ago';
        }

        if (name === 'week' && interval < 4) {
          return `${interval} weeks ago`;
        }

        if (name === 'month' && interval === 1) {
          return '1 month ago';
        }

        if (name === 'month' && interval < 12) {
          return `${interval} months ago`;
        }

        if (name === 'year' && interval === 1) {
          return '1 year ago';
        }

        return `${interval} years ago`;
      }
    }

    return 'Just now';
  }
}
