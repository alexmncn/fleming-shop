import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { catchError, timeout } from 'rxjs/operators';
import { of } from 'rxjs';

import { CatalogService } from '../../../services/catalog/catalog.service';
import { CatalogStoreService } from '../../../services/catalog/catalog-store.service';

import { ArticlesComponent } from '../../../shared/articles/articles.component';
import { FamiliesComponent } from "../../../shared/families/families.component";

@Component({
    selector: 'app-home',
    imports: [CommonModule, ArticlesComponent, FamiliesComponent],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  perPage = this.catalogStore.perPage;

  featuredHeaderTitle = 'Destacado';
  featuredArticles = this.catalogStore.visibleFeaturedArticles;
  totalFeaturedArticles = this.catalogStore.totalFeaturedArticles;
  featuredPage = this.catalogStore.featuredPage;
  featuredOrderBy = this.catalogStore.featuredOrderBy;
  featuredDirection = this.catalogStore.featuredDirection;
  loadingFeatured = this.catalogStore.loadingFeatured;
  featuredStatusCode = this.catalogStore.featuredStatusCode;

  newHeaderTitle: string = 'Novedades';
  newArticles: any[] = [];
  newArticlesPage: number = 1;
  newArticlesOrderBy: string = 'date';
  newArticlesDirection: string = 'desc';
  totalNewArticles: number = 0;
  loadingNewArticles: boolean = false;
  newStatusCode: number = 0;

  constructor(private catalogService: CatalogService, private catalogStore: CatalogStoreService) { }

  ngOnInit(): void {
    // Si no hay artículos, carga todo
    if (this.catalogStore.featuredArticles().length === 0) {
      this.catalogStore.loadTotalFeaturedArticles();
      this.catalogStore.loadFeaturedArticles(true); // reset cache + visiblePages
    } else {
      // Solo reset de ventana visible
      this.catalogStore.visiblePages.set(1);
    }

    this.loadTotalNewArticles();
    this.loadNewArticles();
  }


  onLoadMoreFeatured() {
    this.catalogStore.loadFeaturedArticles(false);
  }


  onSortChangeFeaturedArticles(orderBy: string, direction: string): void {
    this.featuredOrderBy.set(orderBy);
    this.featuredDirection.set(direction);
    this.catalogStore.forceReloadFeatured();
  }
  

  loadTotalNewArticles(): void {
    this.catalogService.getTotalNewArticles().subscribe({
      next: (res) => this.totalNewArticles = res.total,
      error: (err) => {
        this.newStatusCode = err.status || 500;
        console.error('Error fetching total:', err);
      }
    });
  }

  loadNewArticles(): void {
    this.loadingNewArticles = true;
    this.catalogService.getNewArticles(this.newArticlesPage, this.perPage(), this.newArticlesOrderBy, this.newArticlesDirection)
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