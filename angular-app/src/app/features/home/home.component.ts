import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { catchError, timeout } from 'rxjs/operators';
import { of, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';

import { ArticlesService } from '../../services/catalog/articles/articles.service';

import { ArticlesComponent } from '../../shared/articles/articles.component';
import { FamiliesComponent } from "../../shared/families/families.component";

@Component({
    selector: 'app-home',
    imports: [CommonModule, ArticlesComponent, FamiliesComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  perPage: number = 20;

  featuredArticles: any[] = [];
  featuredHeaderTitle: string = 'Destacado';
  featuredArticlesPage: number = 1;
  featuredArticlesOrderBy: string = 'detalle';
  featuredArticlesDirection: string = 'asc';
  totalFeaturedArticles: number = 0;
  loadingFeaturedArticles: boolean = false;
  featuredStatusCode: number = 0;

  newArticlesURL: string = environment.apiUrl + '/articles/new';
  newHeaderTitle: string = 'Novedades';
  newArticles: any[] = [];
  newArticlesPage: number = 1;
  newArticlesOrderBy: string = 'detalle';
  newArticlesDirection: string = 'asc';
  totalNewArticles: number = 0;
  loadingNewArticles: boolean = false;
  newStatusCode: number = 0;

  constructor(private http: HttpClient, private articlesService: ArticlesService) { }

  ngOnInit(): void {
    this.loadTotalFeaturedArticles();
    this.loadFeaturedArticles();

    this.loadTotalNewArticles()
    this.loadNewArticles()
  }


  loadTotalFeaturedArticles(): void {
    this.articlesService.getTotalFeaturedArticles().subscribe({
      next: (res) => this.totalFeaturedArticles = res.total,
      error: (err) => {
        this.featuredStatusCode = err.status || 500;
        console.error('Error fetching total:', err);
      }
    });
  }

  loadFeaturedArticles(): void {
    this.loadingFeaturedArticles = true;
    this.articlesService.getFeaturedArticles(this.featuredArticlesPage, this.perPage, this.featuredArticlesOrderBy, this.featuredArticlesDirection)
      .pipe(
        timeout(10000),
        catchError(err => {
          this.loadingFeaturedArticles = false;
          this.featuredStatusCode = err.status || 500;
          return of([]);
        })
      )
      .subscribe({
        next: (articles) => {
          this.featuredArticles = [...this.featuredArticles, ...articles];
          this.featuredArticlesPage++;
          this.loadingFeaturedArticles = false;
        },
        error: (err) => {
          this.loadingFeaturedArticles = false;
          this.featuredStatusCode = err.status;
        }
      });
  }

  onSortChangeFeaturedArticles(order_by: string, direction: string): void {
    this.featuredArticlesOrderBy = order_by;
    this.featuredArticlesDirection = direction;
    this.featuredArticlesPage = 1;
    this.featuredArticles = [];
    this.loadFeaturedArticles();
  }
  

  loadTotalNewArticles(): void {
    this.articlesService.getTotalNewArticles().subscribe({
      next: (res) => this.totalNewArticles = res.total,
      error: (err) => {
        this.newStatusCode = err.status || 500;
        console.error('Error fetching total:', err);
      }
    });
  }

  loadNewArticles(): void {
    this.loadingNewArticles = true;
    this.articlesService.getNewArticles(this.newArticlesPage, this.perPage, this.newArticlesOrderBy, this.newArticlesDirection)
      .pipe(
        timeout(10000),
        catchError(err => {
          this.loadingNewArticles = false;
          this.newStatusCode = err.status || 500;
          return of([]);
        })
      )
      .subscribe({
        next: (articles) => {
          this.newArticles = [...this.newArticles, ...articles];
          this.newArticlesPage++;
          this.loadingNewArticles = false;
        },
        error: (err) => {
          this.loadingNewArticles = false;
          this.newStatusCode = err.status;
        }
      });
  }

  onSortChangeNewArticles(order_by: string, direction: string): void {
    this.newArticlesOrderBy = order_by;
    this.newArticlesDirection = direction;
    this.newArticlesPage = 1;
    this.newArticles = [];
    this.loadNewArticles();
  }
}