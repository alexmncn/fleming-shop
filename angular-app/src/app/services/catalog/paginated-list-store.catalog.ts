import { signal, computed } from '@angular/core';
import { firstValueFrom, Observable } from 'rxjs';

interface Identifiable {
  id?: string | number;
  codebar?: string;
  codfam?: number;
}

export class PaginatedListStore<T extends Identifiable> {
  // === CONFIGURABLE ===
  private fetchPageFn: (...args: any[]) => Observable<T[]>; // función que pide artículos
  private fetchTotalFn?: (...args: any[]) => Observable<{ total: number }>; // opcional

  // === STATE ===
  perPage = signal(20);
  items = signal<T[]>([]);
  total = signal<number>(0);
  page = signal<number>(1);
  visiblePages = signal<number>(1);
  loading = signal<boolean>(false);
  statusCode = signal<number>(0);

  // parámetros de orden
  orderBy = signal<string>('detalle');
  direction = signal<string>('asc');

  // === COMPUTED ===
  hasMoreRemote = computed(() => this.items().length < this.total());
  visibleCount = computed(() => this.perPage() * this.visiblePages());
  visibleItems = computed(() => this.items().slice(0, this.visibleCount()));
  hasMoreCached = computed(() => this.items().length > this.visibleCount());
  hasMore = computed(() => this.hasMoreCached() || this.hasMoreRemote());

  constructor(fetchPageFn: (...args: any[]) => Observable<T[]>, fetchTotalFn?: (...args: any[]) => Observable<{ total: number }>) {
    this.fetchPageFn = fetchPageFn;
    this.fetchTotalFn = fetchTotalFn;
  }

  // === MÉTODOS ===

  async loadTotal(...args: any[]) {
    if (!this.fetchTotalFn) return;
    try {
      const res = await firstValueFrom(this.fetchTotalFn(...args));
      this.total.set(res.total);
    } catch (err: any) {
      this.statusCode.set(err.status || 500);
    }
  }

  async load(reset = false, ...args: any[]) {
    if (reset) {
      this.items.set([]);
      this.page.set(1);
      this.visiblePages.set(1);
    }

    const cached = this.items();
    const needVisible = this.visibleCount();
    const perPage = this.perPage();
    const nextPageToRequest = this.page();

    // Si ya hay suficientes artículos cacheados para mostrar la siguiente ventana:
    if (cached.length >= needVisible + perPage) {
      this.visiblePages.update(v => v + 1);
      return;
    }

    // Si hay algunos en cache pero aún queda por pedir:
    if (cached.length >= needVisible) {
      this.visiblePages.update(v => v + 1);
      if (!this.hasMoreRemote()) return;
    }

    // Pedir siguiente página
    this.loading.set(true);
    try {
      const data = await firstValueFrom(this.fetchPageFn(nextPageToRequest, perPage, this.orderBy(), this.direction(), ...args));
      if (!Array.isArray(data)) throw new Error('Invalid API response');

      // evitar duplicados
      const existingIds = new Set((cached as any[]).map((a: any) => a.codebar ?? a.codfam ?? a.id ?? JSON.stringify(a)));
      const newOnes = data.filter(a => !existingIds.has(a.codebar ?? a.codfam ?? a.id ?? JSON.stringify(a)));

      if (newOnes.length) {
        this.items.update(current => [...current, ...newOnes]);
      }

      this.page.update(p => p + 1);
      this.visiblePages.update(v => v + 1);
    } catch (err: any) {
      console.error(err);
      this.statusCode.set(err.status || 500);
    } finally {
      this.loading.set(false);
    }
  }

  async forceReload(...args: any[]) {
    this.items.set([]);
    this.page.set(1);
    this.visiblePages.set(1);
    await this.loadTotal(...args);
    await this.load(false, ...args);
  }

  async sort(orderBy: string, direction: string, ...args: any[]) {
    this.orderBy.set(orderBy);
    this.direction.set(direction);
    await this.load(true, ...args);
  }

  clear() {
    this.items.set([]);
    this.total.set(0);
    this.page.set(1);
    this.visiblePages.set(1);
  }
}