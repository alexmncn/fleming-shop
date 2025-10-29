import { CommonModule } from '@angular/common';
import { Component, computed, effect, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { MessageService } from '../../../services/message/message.service';

import { ArticlesComponent } from "../../../shared/articles/articles.component";
import { CatalogStoreService } from '../../../services/catalog/catalog-store.service';

@Component({
    selector: 'app-family',
    imports: [CommonModule, ArticlesComponent],
    templateUrl: './family.component.html',
    styleUrl: './family.component.css'
})
export class FamilyComponent {
  nomfam = '';
  codfam = 0;

  articles = computed(() => this.store()?.visibleItems() ?? []);
  totalArticles = computed(() => this.store()?.total() ?? 0);
  page = computed(() => this.store()?.page() ?? 1);
  perPage = computed(() => this.store()?.perPage() ?? 20);
  orderBy = computed(() => this.store()?.orderBy() ?? '');
  direction = computed(() => this.store()?.direction() ?? 'asc');
  loading = computed(() => this.store()?.loading() ?? false);
  statusCode = computed(() => this.store()?.statusCode() ?? -1);

  store = signal<ReturnType<CatalogStoreService['familyArticles']['getStore']> | null>(null);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private catalogStore: CatalogStoreService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(async params => {
      const param = params.get('codfamSlug') || '';
      this.codfam = +param.split('-')[0];
      if (!this.codfam) {
        this.router.navigate(['/catalog']);
        return;
      }

      const families = this.catalogStore.families.families();
      const family = families.find((f) => f.codfam === this.codfam);

      if (!family) {
        this.messageService.showMessage('error', 'La familia solicitada no existe');
        this.router.navigate(['/catalog']);
        return;
      }

      this.nomfam = family.nomfam;

      // Guardamos el store en el signal
      const familyStore = this.catalogStore.familyArticles.getStore(this.codfam);
      this.store.set(familyStore);

      // Cargamos si está vacío
      if (familyStore.items().length === 0) {
        await familyStore.loadTotal();
        await familyStore.load(true);
      } else {
        familyStore.visiblePages.set(1);
      }
    });
  }


  onLoadMoreArticles() {
    this.store()?.load(false);
  }

  onSortChangeArticles(orderBy: string, direction: string): void {
    const s = this.store();
    if (!s) return;
    s.orderBy.set(orderBy);
    s.direction.set(direction);
    s.forceReload();
  }
}