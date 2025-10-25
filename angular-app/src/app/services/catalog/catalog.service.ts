import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { catchError, of, timeout, throwError } from 'rxjs';

import { Article } from '../../models/article.model';
import { Family } from '../../models/family.model';

@Injectable({ providedIn: 'root' })
export class CatalogService {
  private baseUrl = environment.apiUrl;
  private totalArticlesUrl: string = environment.apiUrl + '/articles/total';
  private featuredArticlesUrl: string = this.baseUrl + '/articles/featured';
  private featuredArticlesTotalUrl: string = this.featuredArticlesUrl + '/total';
  private newArticlesUrl: string = this.baseUrl + '/articles/new';
  private newArticlesTotalUrl: string = this.newArticlesUrl + '/total';
  private familiesUrl: string = this.baseUrl + '/articles/families';
  private familiesTotalUrl: string = this.familiesUrl + '/total';
  private searchUrl: string = environment.apiUrl + '/articles/search';
  private searchTotalUrl: string = this.searchUrl + '/total';

  private timeoutDuration = 5000; // 5 seconds

  constructor(private http: HttpClient) {}


  getTotalArticles() {
    return this.http.get<{ total: number }>(this.totalArticlesUrl);
  }

  getTotalFeaturedArticles() {
    return this.http.get<{ total: number }>(this.featuredArticlesTotalUrl);
  }

  getFeaturedArticles(page: number, perPage: number, order_by: string, direction: string) {
    const rawParams: any = {
      ...(page !== undefined ? { page } : {}),
      ...(perPage !== undefined ? { per_page: perPage } : {}),
      ...(order_by && { order_by }),
      ...(direction && { direction })
    };

    const params = new HttpParams({ fromObject: rawParams });

    return this.http.get<Article[]>(this.featuredArticlesUrl, { params }).pipe(
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


  getTotalNewArticles() {
    return this.http.get<{ total: number }>(this.newArticlesTotalUrl);
  }

  getNewArticles(page: number, perPage: number, order_by: string, direction: string) {
    const rawParams: any = {
      ...(page !== undefined ? { page } : {}),
      ...(perPage !== undefined ? { per_page: perPage } : {}),
      ...(order_by && { order_by }),
      ...(direction && { direction })
    };

    const params = new HttpParams({ fromObject: rawParams });

    return this.http.get<Article[]>(this.newArticlesUrl, { params }).pipe(
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


  getTotalFamilies() {
    return this.http.get<{ total: number }>(this.familiesTotalUrl);
  }

  getFamilies(){
    return this.http.get<Family[]>(this.familiesUrl).pipe(
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


  getTotalFamilyArticles(codfam: number) {
    return this.http.get<{ total: number }>(this.familiesUrl + '/' + codfam + '/total');
  }

  getFamilyArticles(codfam: number, page: number, perPage: number, order_by: string, direction: string) {
    const rawParams: any = {
      ...(page !== undefined ? { page } : {}),
      ...(perPage !== undefined ? { per_page: perPage } : {}),
      ...(order_by && { order_by }),
      ...(direction && { direction })
    };

    const params = new HttpParams({ fromObject: rawParams });

    return this.http.get<Article[]>(this.familiesUrl + '/' + codfam, { params }).pipe(
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
  

  getTotalSearchArticles(search: string, filter: string, contextFilter: string, contextValue: string) {
    const rawParams: any = {
      search,
      filter,
      ...(contextFilter && { context_filter: contextFilter }),
      ...(contextValue && { context_value: contextValue }),
    };

    const params = new HttpParams({ fromObject: rawParams });

    return this.http.get<{ total: number }>(this.searchTotalUrl, { params });
  }

  getSearchArticles(search: string, filter: string, contextFilter: string, contextValue: string, page: number, perPage: number, order_by: string, direction: string) {
    const rawParams: any = {
      search,
      filter,
      ...(contextFilter && { context_filter: contextFilter }),
      ...(contextValue && { context_value: contextValue }),
      ...(page !== undefined ? { page } : {}),
      ...(perPage !== undefined ? { per_page: perPage } : {}),
      ...(order_by && { order_by }),
      ...(direction && { direction })
    };

    const params = new HttpParams({ fromObject: rawParams });

    return this.http.get<Article[]>(this.searchUrl, { params }).pipe(
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