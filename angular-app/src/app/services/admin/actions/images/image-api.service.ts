import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../../../environments/environment';
import { catchError, of, throwError, timeout } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class ImageApiService {
  private baseUrl = environment.apiUrl;
  private uploadImageURL: string = this.baseUrl + '/images/articles/upload';

  private timeoutDuration = 10000;

  constructor(private http: HttpClient) {}

  uploadArticleImage(codebar: string, file: File, isMain: boolean) {
    const formData = new FormData();
      formData.append('file', file, file.name);
      formData.append('codebar', codebar);
      formData.append('is_main', isMain ? '1' : '0');

    return this.http.post<{ image_url: string }>(this.uploadImageURL, formData).pipe(
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
