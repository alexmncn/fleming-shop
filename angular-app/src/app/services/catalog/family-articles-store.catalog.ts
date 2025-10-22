import { Injectable } from '@angular/core';
import { CatalogService } from './catalog.service';
import { PaginatedListStore } from './paginated-list-store.catalog';
import { Article } from '../../models/article.model';
import { signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class FamilyArticlesStore {
  perPage = 20;

  // clave: codfam
  stores = signal<Record<number, PaginatedListStore<Article>>>({});

  constructor(private api: CatalogService) {}

  getStore(codfam: number) {
    if (!this.stores()[codfam]) {
      const store = new PaginatedListStore<Article>(
        (page, perPage, orderBy, direction) =>
          this.api.getFamilyArticles(codfam, page, perPage, orderBy, direction),

        () =>
          this.api.getTotalFamilyArticles(codfam)
      );

      this.stores.update(f => ({ ...f, [codfam]: store }));
    }

    return this.stores()[codfam];
  }
}