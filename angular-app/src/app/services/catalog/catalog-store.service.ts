import { inject, Injectable } from '@angular/core';
import { CatalogApiService } from './catalog-api.service';
import { Article } from '../../models/article.model';

import { PaginatedListStore } from './paginated-list-store.catalog';
import { FamilyArticlesStore } from './family-articles-store.catalog';
import { FamilyStore } from './family-store.catalog';

@Injectable({
  providedIn: 'root'
})
export class CatalogStoreService {
  constructor(private api: CatalogApiService) {}

  featuredArticles = new PaginatedListStore<Article>(
    (page, perPage, orderBy, direction) =>
      this.api.getFeaturedArticles(page, perPage, orderBy, direction),
    () => this.api.getTotalFeaturedArticles()
  );

  newArticles = new PaginatedListStore<Article>(
    (page, perPage, orderBy, direction) =>
      this.api.getNewArticles(page, perPage, orderBy, direction),
    () => this.api.getTotalNewArticles()
  );

  families = inject(FamilyStore);

  familyArticles = inject(FamilyArticlesStore);
}
