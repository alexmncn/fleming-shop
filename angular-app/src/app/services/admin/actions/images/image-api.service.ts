import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of, throwError, timeout } from 'rxjs';

import { environment } from '../../../../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class ImageApiService {
  private baseUrl = environment.apiUrl;
  private uploadImageURL: string = this.baseUrl + '/images/articles/upload';
  private getImageURL: string = this.baseUrl + '/images/articles';
  private getAllImagesURL: string = this.baseUrl + '/images/articles/all';

  private timeoutDuration = 10000;

  constructor(private http: HttpClient) {}

  uploadArticleImage(codebar: string, file: File, isMain: boolean): Observable<{ image_url: string }> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('codebar', codebar);
    formData.append('is_main', isMain ? '1' : '0');

    return this.http.post<{ image_url: string }>(this.uploadImageURL, formData).pipe(
      timeout(this.timeoutDuration),
      catchError(error => {
        if (error.name === 'TimeoutError') {
          console.error('Request timed out');
          return of({ image_url: '' });
        }
        const status = error.status || 500;
        const message = error.message || 'An unknown error occurred';
        return throwError(() => ({ status, message }));
      })
    );
  }

  getImageById(imageId: string) {
    const url = this.getImageURL + '/' + imageId;
    return this.http.get(url, { responseType: 'blob' }).pipe(
      timeout(this.timeoutDuration),
      catchError(error => of(null)) // en caso de error devolvemos null
    );
  }
}