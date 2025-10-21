import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { catchError, timeout } from 'rxjs/operators';
import { of } from 'rxjs';

import { ArticlesService } from '../../../services/catalog/articles/articles.service';
import { ArticlesStoreService } from '../../../services/catalog/articles/articles-store.service';

import { ArticlesComponent } from '../../../shared/articles/articles.component';
import { FamiliesComponent } from "../../../shared/families/families.component";

@Component({
    selector: 'app-home',
    imports: [CommonModule, ArticlesComponent, FamiliesComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  perPage = this.articlesStore.perPage;

  featuredHeaderTitle = 'Destacado';
  featuredArticles = this.articlesStore.visibleFeaturedArticles;
  totalFeaturedArticles = this.articlesStore.totalFeaturedArticles;
  featuredPage = this.articlesStore.featuredPage;
  featuredOrderBy = this.articlesStore.featuredOrderBy;
  featuredDirection = this.articlesStore.featuredDirection;
  loadingFeatured = this.articlesStore.loadingFeatured;
  featuredStatusCode = this.articlesStore.featuredStatusCode;

  newHeaderTitle: string = 'Novedades';
  newArticles: any[] = [];
  newArticlesPage: number = 1;
  newArticlesOrderBy: string = 'date';
  newArticlesDirection: string = 'desc';
  totalNewArticles: number = 0;
  loadingNewArticles: boolean = false;
  newStatusCode: number = 0;

  constructor(private articlesService: ArticlesService, private articlesStore: ArticlesStoreService) { }

  ngOnInit(): void {
    // Si no hay artículos, carga todo
    if (this.articlesStore.featuredArticles().length === 0) {
      this.articlesStore.loadTotalFeaturedArticles();
      this.articlesStore.loadFeaturedArticles(true); // reset cache + visiblePages
    } else {
      // Solo reset de ventana visible
      this.articlesStore.visiblePages.set(1);
    }

    this.loadTotalNewArticles();
    this.loadNewArticles();
  }


  onLoadMoreFeatured() {
    this.articlesStore.loadFeaturedArticles(false);
  }


  onSortChangeFeaturedArticles(orderBy: string, direction: string): void {
    this.featuredOrderBy.set(orderBy);
    this.featuredDirection.set(direction);
    this.articlesStore.forceReloadFeatured();
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
    this.articlesService.getNewArticles(this.newArticlesPage, this.perPage(), this.newArticlesOrderBy, this.newArticlesDirection)
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