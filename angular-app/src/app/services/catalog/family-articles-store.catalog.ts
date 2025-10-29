import { Injectable, signal } from '@angular/core';
import { CatalogApiService } from './catalog-api.service';
import { PaginatedListStore } from './paginated-list-store.catalog';

@Injectable({ providedIn: 'root' })
export class FamilyArticlesStore {
  perPage = 20;

  // clave: codfam
  stores = signal<Record<number, PaginatedListStore>>({});

  constructor(private api: CatalogApiService) {}

  getStore(codfam: number): PaginatedListStore {
    const existing = this.stores()[codfam];
    if (existing) return existing;

    const store = new PaginatedListStore(
      (page, perPage, orderBy, direction) =>
        this.api.getFamilyArticles(codfam, page, perPage, orderBy, direction),
      () => this.api.getTotalFamilyArticles(codfam)
    );

    this.stores.update(f => ({ ...f, [codfam]: store }));
    return store;
  }
}