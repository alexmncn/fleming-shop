import { Component, computed, signal } from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';

import { MessageService } from '../../../services/message/message.service';

import { ArticlesComponent } from "../../../shared/articles/articles.component";
import { CatalogStoreService } from '../../../services/catalog/catalog-store.service';
import { PaginatedListStore } from '../../../services/catalog/paginated-list-store.catalog';

@Component({
    selector: 'app-family',
    imports: [ArticlesComponent],
    templateUrl: './family.component.html',
    styleUrl: './family.component.css'
})
export class FamilyComponent {
  nomfam: string = '';
  codfam: number = 0;

  store = signal<PaginatedListStore | undefined>(undefined);

  articles = computed(() => this.store()?.visibleItems() ?? []);
  totalArticles = computed(() => this.store()?.total() ?? 0);
  page = computed(() => this.store()?.page() ?? 1);
  perPage = computed(() => this.store()?.perPage() ?? 20);
  orderBy = computed(() => this.store()?.orderBy() ?? '');
  direction = computed(() => this.store()?.direction() ?? 'asc');
  loading = computed(() => this.store()?.loading() ?? false);
  statusCode = computed(() => this.store()?.statusCode() ?? -1);

  constructor(private route: ActivatedRoute, private router: Router, private catalogStore: CatalogStoreService, private messageService: MessageService) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(async params => {
      const param = params.get('codfamSlug') || '';
      this.codfam = +param.split('-')[0];
      if (!this.codfam) {
        this.router.navigate(['/catalog']);
        return;
      }

      this.loadFamilyData();
    });
  }

  private async loadFamilyData(): Promise<void> {
    let families = this.catalogStore.families.families();
    if (families.length === 0) {
      await this.catalogStore.families.loadTotal();
      await this.catalogStore.families.load();
      families = this.catalogStore.families.families();
    }
    
    const family = families.find((f) => f.codfam === this.codfam);
    if (!family) {
      // Si no existe, redirige
      this.messageService.showMessage('error', 'La familia solicitada no existe');
      this.router.navigate(['/catalog']);
      return;
    }

    this.nomfam = family.nomfam;

    // Obtiene el store asociado a esta familia
    const familyStore = this.catalogStore.familyArticles.getStore(this.codfam);
    this.store.set(familyStore);

    // Si aún no se ha cargado nada, haz una carga inicial
    if (this.store()?.items().length === 0) {
      this.store()?.loadTotal();
      this.store()?.load(true);
    } else {
      // Si ya hay datos, reinicia la vista al principio
      this.store()?.visiblePages.set(1);
    }
  }

  onLoadMoreArticles() {
    this.store()?.load(false);
  }

  onSortChangeArticles(orderBy: string, direction: string): void {
    this.store()?.orderBy.set(orderBy);
    this.store()?.direction?.set(direction);
    this.store()?.forceReload();
  }
}