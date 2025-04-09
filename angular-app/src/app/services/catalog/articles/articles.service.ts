import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { catchError, of, timeout, throwError } from 'rxjs';
import { Article } from '../../../models/article.model';

@Injectable({ providedIn: 'root' })
export class ArticlesService {
  private baseUrl = environment.apiUrl;
  private featuredArticlesUrl = this.baseUrl + '/articles/featured';
  private featuredArticlesTotalUrl = this.featuredArticlesUrl + '/total';
  private newArticlesUrl = this.baseUrl + '/articles/new';
  private newArticlesTotalUrl = this.newArticlesUrl + '/total';

  constructor(private http: HttpClient) {}

  getTotalFeaturedArticles() {
    return this.http.get<{ total: number }>(this.featuredArticlesTotalUrl);
  }

  getFeaturedArticles(page: number, perPage: number, order_by = 'detalle', direction = 'asc') {
    const params = new HttpParams()
      .set('page', page)
      .set('per_page', perPage)
      .set('order_by', order_by)
      .set('direction', direction);

    return this.http.get<Article[]>(this.featuredArticlesUrl, { params }).pipe(
      timeout(10000),
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


  getTotalNewArticles() {
    return this.http.get<{ total: number }>(this.newArticlesTotalUrl);
  }

  getNewArticles(page: number, perPage: number, order_by = 'detalle', direction = 'asc') {
    const params = new HttpParams()
      .set('page', page)
      .set('per_page', perPage)
      .set('order_by', order_by)
      .set('direction', direction);

    return this.http.get<Article[]>(this.newArticlesUrl, { params }).pipe(
      timeout(10000),
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