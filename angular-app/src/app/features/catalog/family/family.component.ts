import { Component, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
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
  nomfam: string = '';
  codfam: number = 0;

  store?: ReturnType<CatalogStoreService['familyArticles']['getStore']>;

  articles = computed(() => this.store?.visibleItems() ?? []);
  totalArticles = computed(() => this.store?.total() ?? 0);
  page = computed(() => this.store?.page() ?? 1);
  perPage = computed(() => this.store?.perPage() ?? 20);
  orderBy = computed(() => this.store?.orderBy() ?? '');
  direction = computed(() => this.store?.direction() ?? 'asc');
  loading = computed(() => this.store?.loading() ?? false);
  statusCode = computed(() => this.store?.statusCode() ?? -1);

  constructor(private route: ActivatedRoute, private router: Router, private catalogStore: CatalogStoreService, private messageService: MessageService) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(async (params) => {
      this.nomfam = params['nomfam'];
      this.codfam = +params['codfam'];

      // Valida que la familia exista
      const validFamily = this.catalogStore.families.families()
        .find(f => f.codfam === this.codfam && f.nomfam === this.nomfam);

      if (!validFamily) {
        this.messageService.showMessage('error', 'La familia solicitada no existe.');
        this.router.navigate(['/catalog']);
        return;
      }

      // Obtiene el store asociado a esta familia
      this.store = this.catalogStore.familyArticles.getStore(this.codfam);

      // Si aún no se ha cargado nada, haz una carga inicial
      if (this.store.items().length === 0) {
        await this.store.loadTotal();
        await this.store.load(true);
      } else {
        // Si ya hay datos, reinicia la vista al principio
        this.store.visiblePages.set(1);
      }
    });
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