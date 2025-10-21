import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

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
  perPage = this.catalogStore.featuredArticles.perPage;

  featuredHeaderTitle = 'Destacado';
  featuredArticles = this.catalogStore.featuredArticles.visibleItems;
  totalFeaturedArticles = this.catalogStore.featuredArticles.total;
  featuredPage = this.catalogStore.featuredArticles.page;
  featuredOrderBy = this.catalogStore.featuredArticles.orderBy;
  featuredDirection = this.catalogStore.featuredArticles.direction;
  loadingFeatured = this.catalogStore.featuredArticles.loading;
  featuredStatusCode = this.catalogStore.featuredArticles.statusCode;

  newHeaderTitle: string = 'Novedades';
  newArticles = this.catalogStore.newArticles.visibleItems;
  totalNewArticles = this.catalogStore.newArticles.total;
  newPage = this.catalogStore.newArticles.page;
  newOrderBy = this.catalogStore.newArticles.orderBy;
  newDirection = this.catalogStore.newArticles.direction;
  loadingNew = this.catalogStore.newArticles.loading;
  newStatusCode = this.catalogStore.newArticles.statusCode;

  constructor(private catalogStore: CatalogStoreService) { }

  ngOnInit(): void {
    // Si no hay artículos, carga todo
    if (this.catalogStore.featuredArticles.items().length === 0) {
      this.catalogStore.featuredArticles.loadTotal();
      this.catalogStore.featuredArticles.load(true);
    } else {
      // Solo reset de ventana visible
      this.catalogStore.featuredArticles.visiblePages.set(1);
    }

    if (this.catalogStore.newArticles.items().length === 0) {
      this.catalogStore.newArticles.loadTotal();
      this.catalogStore.newArticles.load(true);
    } else {
      // Solo reset de ventana visible
      this.catalogStore.newArticles.visiblePages.set(1);
    }
  }


  onLoadMoreFeaturedArticles() {
    this.catalogStore.featuredArticles.load(false);
  }


  onSortChangeFeaturedArticles(orderBy: string, direction: string): void {
    this.featuredOrderBy.set(orderBy);
    this.featuredDirection.set(direction);
    this.catalogStore.featuredArticles.forceReload();
  }
  

  onLoadMoreNewArticles() {
    this.catalogStore.newArticles.load(false);
  }


  onSortChangeNewArticles(orderBy: string, direction: string): void {
    this.newOrderBy.set(orderBy);
    this.newDirection.set(direction);
    this.catalogStore.newArticles.forceReload();
  }
}