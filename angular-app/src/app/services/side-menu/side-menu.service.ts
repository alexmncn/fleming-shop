import { Injectable, signal, computed, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { fromEvent, Subscription } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SideMenuService implements OnDestroy {
  isOpen = signal(false);
  isScreenSmall = signal(window.innerWidth <= 600);
  currentUrl = signal<string>('/');

  isDrawer = computed(() => this.isScreenSmall() || this.currentUrl().startsWith('/catalog/'));

  private resizeSub?: Subscription;
  private routerSub?: Subscription;

  constructor(private router: Router) {
    this.currentUrl.set(this.router.url || '/');

    // Subscribe a eventos de navegación para mantener currentUrl actualizado
    this.routerSub = this.router.events
      .pipe(filter(e => e instanceof NavigationEnd))
      .subscribe((e: any) => this.currentUrl.set(e.urlAfterRedirects ?? e.url));

    // Escucha resize con RxJS
    this.resizeSub = fromEvent(window, 'resize').subscribe(() => {
      this.isScreenSmall.set(window.innerWidth <= 600);
    });
  }

  open() { this.isOpen.set(true); }
  close() { this.isOpen.set(false); }
  toggle() { this.isOpen.update(v => !v); }

  ngOnDestroy(): void {
    this.resizeSub?.unsubscribe();
    this.routerSub?.unsubscribe();
  }
}