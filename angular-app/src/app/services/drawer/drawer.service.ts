import { Injectable, signal, HostListener } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class DrawerService {
  drawerOpen = signal(false);
  isScreenSmall: boolean = window.innerWidth <= 600;

  constructor(private router: Router) {}

  get atCatalog(): boolean {
    return this.router.url.startsWith('/catalog/');
  }

  get isDrawer(): boolean {
    return this.isScreenSmall || this.atCatalog;
  }

  open() {
    this.drawerOpen.set(true);
  }

  close() {
    this.drawerOpen.set(false);
  }

  toggle() {
    this.drawerOpen.update(v => !v);
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: Event) {
    this.isScreenSmall = window.innerWidth <= 600;
  }
}