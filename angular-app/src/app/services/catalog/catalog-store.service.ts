import { Injectable, signal, computed } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { CatalogService } from './catalog.service';
import { Article } from '../../models/article.model';

@Injectable({
  providedIn: 'root'
})
export class CatalogStoreService {
  // ====== STATE SIGNALS ======
  perPage = signal(20)

  featuredArticles = signal<Article[]>([]);
  totalFeaturedArticles = signal<number>(0);
  featuredPage = signal<number>(1);
  visiblePages = signal<number>(1); 
  featuredOrderBy = signal<string>('detalle');
  featuredDirection = signal<string>('asc');
  loadingFeatured = signal<boolean>(false);
  featuredStatusCode = signal<number>(0);

  // ====== COMPUTED (DERIVED STATE) ======
  hasMoreFeatured = computed(
    () => this.featuredArticles().length < this.totalFeaturedArticles()
  );

  // ====== DERIVADOS ======
  // número de artículos visibles actualmente
  visibleCount = computed(() => this.perPage() * this.visiblePages());

  // array de artículos que se pasan al componente (slice de cache)
  visibleFeaturedArticles = computed(() =>
    this.featuredArticles().slice(0, this.visibleCount())
  );

  // si ya se han cargado todos los artículos conocidos vs total declarado
  hasMoreCached = computed(() => this.featuredArticles().length > this.visibleCount());
  // si según el total declarado quedan más por pedir al backend
  hasMoreRemote = computed(() => this.featuredArticles().length < this.totalFeaturedArticles());

  constructor(private api: CatalogService) {}

  // carga total (si tu endpoint lo usa)
  async loadTotalFeaturedArticles() {
    try {
      const res = await firstValueFrom(this.api.getTotalFeaturedArticles());
      this.totalFeaturedArticles.set(res.total);
    } catch (err: any) {
      this.featuredStatusCode.set(err.status || 500);
    }
  }

  // ====== FUNCION PRINCIPAL: solicita nueva página SOLO si hace falta ======
  async loadFeaturedArticles(reset = false) {
    if (reset) {
      this.featuredArticles.set([]);
      this.featuredPage.set(1);     // pediremos la página 1
      this.visiblePages.set(1);     // mostramos solo la primera página
    }

    const cached = this.featuredArticles();
    const needVisible = this.visibleCount();
    const perPage = this.perPage();
    const nextPageToRequest = this.featuredPage();

    // 1) Si ya hay suficientes artículos cacheados para aumentar la ventana:
    if (cached.length >= needVisible + perPage) {
      // solo ampliamos la ventana visible (no petición)
      this.visiblePages.update(v => v + 1);
      return;
    }

    // 2) Si hay artículos cacheados pero insuficientes para cubrir la próxima ventana,
    //    podemos aumentar visiblePages si esos artículos alcanzan la ventana actual.
    if (cached.length >= needVisible) {
      this.visiblePages.update(v => v + 1);
      // pero todavía no hay datos remotos que pedir → devolvemos
      if (!this.hasMoreRemote()) return;
    }

    // 3) Si llegamos aquí, necesitamos pedir la siguiente página al backend.
    //    Asegúrate de que nextPageToRequest no supere el total de páginas (opcional).
    this.loadingFeatured.set(true);
    try {
      const articles = await firstValueFrom(
        this.api.getFeaturedArticles(nextPageToRequest, perPage, this.featuredOrderBy(), this.featuredDirection())
      );

      // evitar duplicados por si el backend devolviera overlaps
      const existingIds = new Set(cached.map(a => a.codebar));
      const newOnes = articles.filter(a => !existingIds.has(a.codebar));

      // cacheamos los nuevos
      if (newOnes.length) {
        this.featuredArticles.update(current => [...current, ...newOnes]);
      }

      // incrementamos página y también la ventana visible (nueva página mostrada)
      this.featuredPage.update(p => p + 1);
      this.visiblePages.update(v => v + 1);
    } catch (err: any) {
      this.featuredStatusCode.set(err.status || 500);
    } finally {
      this.loadingFeatured.set(false);
    }
  }

  // Forzar recarga completa (por ejemplo tras cambiar el orden)
  async forceReloadFeatured() {
    this.featuredArticles.set([]);
    this.featuredPage.set(1);
    this.visiblePages.set(1);
    await this.loadTotalFeaturedArticles();
    await this.loadFeaturedArticles(false);
  }

  async sortFeatured(orderBy: string, direction: string) {
    this.featuredOrderBy.set(orderBy as any);
    this.featuredDirection.set(direction as any);
    await this.loadFeaturedArticles(true);
  }

  clearFeatured() {
    this.featuredArticles.set([]);
    this.totalFeaturedArticles.set(0);
    this.featuredPage.set(1);
  }
}
