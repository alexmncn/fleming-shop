import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../../../environments/environment';
import { catchError, of, throwError, timeout } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ArticleActionsApiService {
  private baseUrl = environment.apiUrl;
  private featureURL: string = this.baseUrl + '/articles/feature';
  private hideURL: string = this.baseUrl + '/articles/hide';

  private timeoutDuration = 10000; // 10 seconds

  constructor(private http: HttpClient) {}

  featureArticle(codebar: string, newValue: boolean) {
    return this.http.post(this.featureURL, {},{params: {'codebar': codebar, 'featured': newValue}}).pipe(
      timeout(this.timeoutDuration),
      catchError(error => {
        if (error.name === 'TimeoutError') {
          console.error('Request timed out');
          return of([]);
        }
        const status = error.status || 500;
        const message = error.message || 'An unknown error occurred';
        return throwError(() => ({ status, message }));
      })
    );
  }

  hideArticle(codebar: string, newValue: boolean) {
    return this.http.post(this.hideURL, {},{params: {'codebar': codebar, 'hidden': newValue}}).pipe(
      timeout(this.timeoutDuration),
      catchError(error => {
        if (error.name === 'TimeoutError') {
          console.error('Request timed out');
          return of([]);
        }
        const status = error.status || 500;
        const message = error.message || 'An unknown error occurred';
        return throwError(() => ({ status, message }));
      })
    );
  }
}
