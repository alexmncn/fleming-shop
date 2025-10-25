import { Component, computed } from '@angular/core';

import { ArticlesComponent } from '../../../shared/articles/articles.component';

import { CatalogStoreService } from '../../../services/catalog/catalog-store.service';

@Component({
  selector: 'app-new',
  imports: [ArticlesComponent],
  templateUrl: './new.component.html',
  styleUrl: './new.component.css'
})
export class NewComponent {
  store = this.catalogStore.newArticles;

  headerTitle = 'Novedades';
  articles = computed(() => this.store?.visibleItems() ?? []);
  totalArticles = computed(() => this.store?.total() ?? 0);
  page = computed(() => this.store?.page() ?? 1);
  perPage = computed(() => this.store?.perPage() ?? 20);
  orderBy = computed(() => this.store?.orderBy() ?? '');
  direction = computed(() => this.store?.direction() ?? 'asc');
  loading = computed(() => this.store?.loading() ?? false);
  statusCode = computed(() => this.store?.statusCode() ?? -1);

  constructor(private catalogStore: CatalogStoreService) {}

  ngOnInit(): void {
    // Si no hay artículos, carga todo
    if (this.store?.items().length === 0) {
      this.store?.loadTotal();
      this.store?.load(true);
    } else {
      // Solo reset de ventana visible
      this.store?.visiblePages.set(1);
    }
  }

  onLoadMoreArticles() {
    this.store?.load(false);
  }

  onSortChangeArticles(orderBy: string, direction: string): void {
    this.store?.orderBy.set(orderBy);
    this.store?.direction?.set(direction);
    this.store?.forceReload();
  }
}
