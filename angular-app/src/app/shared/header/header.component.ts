import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { MatIcon } from '@angular/material/icon';

import { AuthService } from '../../services/auth/auth.service';
import { DrawerService } from '../../services/drawer/drawer.service';

@Component({
    selector: 'app-header',
    imports: [RouterLink, CommonModule, MatIcon],
    templateUrl: './header.component.html',
    styleUrl: './header.component.css'
})
export class HeaderComponent implements OnInit {
  isScreenSmall: boolean = window.innerWidth <= 600;
  isAuth: boolean = false;
  username: string | null = '';

  constructor(private router: Router, private authService: AuthService, public drawerService: DrawerService) {}

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth = auth;
    });

    this.authService.username$.subscribe((name: string | null) => {
      this.username = name;
    });
    
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: Event) {
    this.isScreenSmall = window.innerWidth <= 600;
  }

  toggleSideMenu(e: Event) {
    e.stopPropagation()
    this.drawerService.toggle();
  }

  get atCatalog(): boolean {
    return this.router.url.startsWith('/catalog/');
  }
}