import { Component, OnInit, HostListener, signal } from '@angular/core';

import { Router, RouterLink } from '@angular/router';

import { SearchBarComponent } from '../search-bar/search-bar.component';

import { AuthService } from '../../services/auth/auth.service';
import { SideMenuService } from '../../services/side-menu/side-menu.service';
import { fromEvent, Subscription } from 'rxjs';

@Component({
    selector: 'app-header',
    imports: [RouterLink, SearchBarComponent],
    templateUrl: './header.component.html',
    styleUrl: './header.component.css'
})
export class HeaderComponent implements OnInit {
  isScreenSmall = signal(window.innerWidth <= 600);
  isAuth: boolean = false;
  username: string | null = '';

  private resizeSub?: Subscription;

  constructor(private router: Router, private authService: AuthService, public sideMenuService: SideMenuService) {
    // Escucha resize con RxJS
    this.resizeSub = fromEvent(window, 'resize').subscribe(() => {
      this.isScreenSmall.set(window.innerWidth <= 600);
    });
  }

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth = auth;
    });

    this.authService.username$.subscribe((name: string | null) => {
      this.username = name;
    });
    
  }

  toggleSideMenu(e: Event) {
    e.stopPropagation()
    this.sideMenuService.toggle();
  }

  get atCatalog(): boolean {
    return this.router.url.startsWith('/catalog/');
  }
}