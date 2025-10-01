import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class DrawerService {
  drawerOpen = signal(false);

  open() {
    this.drawerOpen.set(true);
  }

  close() {
    this.drawerOpen.set(false);
  }

  toggle() {
    this.drawerOpen.update(v => !v);
  }
}