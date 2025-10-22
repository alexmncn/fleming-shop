import { inject, Injectable } from '@angular/core';
import { CatalogService } from './catalog.service';
import { Article } from '../../models/article.model';
import { Family } from '../../models/family.model';

import { PaginatedListStore } from './paginated-list-store.catalog';
import { FamilyArticlesStore } from './family-articles-store.catalog';
import { FamilyStore } from './family-store.catalog';

@Injectable({
  providedIn: 'root'
})
export class CatalogStoreService {
  constructor(private api: CatalogService) {}

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
