import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { catchError, timeout } from 'rxjs/operators';
import { of, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';

import { ArticlesComponent } from '../../shared/articles/articles.component';
import { FamiliesComponent } from "../../shared/families/families.component";

@Component({
    selector: 'app-home',
    imports: [CommonModule, ArticlesComponent, FamiliesComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  per_page: number = 20;

  featuredArticlesURL: string = environment.apiUrl + '/articles/featured';
  featuredArticles: any[] = [];
  featuredHeaderTitle: string = 'Destacado';
  featuredArticlesPage: number = 1;
  totalFeaturedArticles: number = 0;
  loadingFeaturedArticles: boolean = false;
  featuredStatusCode: number = 0;

  newArticlesURL: string = environment.apiUrl + '/articles/new';
  newHeaderTitle: string = 'Novedades';
  newArticles: any[] = [];
  newArticlesPage: number = 1;
  totalNewArticles: number = 0;
  loadingNewArticles: boolean = false;
  newStatusCode: number = 0;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.getTotalFeaturedArticles()
    this.getTotalNewArticles()

    this.loadFeaturedArticles()
    this.loadNewArticles()
  }

  getTotalFeaturedArticles(): void {
    this.http.get<any>(this.featuredArticlesURL + '/total')
      .subscribe((data) => {
        this.totalFeaturedArticles = data.total;
      });
  }

  loadFeaturedArticles(): void {
    this.loadingFeaturedArticles = true;
    this.http.get(this.featuredArticlesURL, {params: {'page': this.featuredArticlesPage, 'per_page': this.per_page}})
      .pipe(
        timeout(10000),
        catchError(error => {
          this.loadingFeaturedArticles = false;
          if (error.name === 'TimeoutError') {
            console.error('Request timed out');
            this.featuredStatusCode = 408;
            return of([]);
          }
          const status = error.status || 500;
          const message = error.message || 'An unknown error occurred';

          return throwError(() => ({
            status,
            message
          }));
        })
      )
      .subscribe({
        next: (response) => {
          this.featuredArticles = this.featuredArticles.concat(response);
          this.featuredArticlesPage++;

          this.loadingFeaturedArticles = false;
        },
        error: (error) => {
          this.loadingFeaturedArticles = false;
          this.featuredStatusCode = error.status;
        },
        complete: () => {
        }
      });
  }
  
  getTotalNewArticles(): void {
    this.http.get<any>(this.newArticlesURL + '/total')
      .subscribe((data) => {
        this.totalNewArticles = data.total;
      });
  }

  loadNewArticles(): void {
  this.loadingNewArticles = true;
    this.http.get(this.newArticlesURL, {params: {'page': this.newArticlesPage, 'per_page': this.per_page}})
      .pipe(
        timeout(10000),
        catchError(error => {
          this.loadingNewArticles = false;
          if (error.name === 'TimeoutError') {
            console.error('Request timed out');
            this.newStatusCode = 408;
            return of([]);
          }
          const status = error.status || 500;
          const message = error.message || 'An unknown error occurred';

          return throwError(() => ({
            status,
            message
          }));
        })
      )
      .subscribe({
        next: (response) => {
          this.newArticles = this.newArticles.concat(response);
          this.newArticlesPage++;

          this.loadingNewArticles = false;
        },
        error: (error) => {
          this.loadingNewArticles = false;
          this.newStatusCode = error.status;
        },
        complete: () => {
        }
      });
  }
}