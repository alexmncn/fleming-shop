import { Component, effect, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';
import { SideMenuService } from '../../services/side-menu/side-menu.service';

@Component({
  selector: 'app-side-menu',
  imports: [],
  templateUrl: './side-menu.component.html',
  styleUrl: './side-menu.component.css'
})
export class SideMenuComponent {
  isAuth: boolean = false;
  currentRoute: string = "";
  drawerVisible = signal(false);

  menuItems = [
    { label: 'Catálogo', icon: 'pi pi-home', routerLink: '/catalog' },
    { label: 'Artículos', icon: 'pi pi-box', routerLink: '/admin/articles' },
    { label: 'Familias', icon: 'pi pi-tags', routerLink: '/admin/families' },
    { label: 'Ventas', icon: 'pi pi-dollar', routerLink: '/admin/sales' },
    { label: 'Estadísticas', icon: 'pi pi-chart-bar', routerLink: '/admin/statistics' },
    { label: 'Imágenes', icon: 'pi pi-image', routerLink: '/admin/images' },
    { label: 'Importar datos', icon: 'pi pi-file-import', routerLink: '/admin/data-import' },
    { label: 'Exportar datos', icon: 'pi pi-file-export', routerLink: '/admin/data-export' }    
  ];

  constructor(private authService: AuthService, private router: Router, private messageService: MessageService, public sideMenuService: SideMenuService) {
    effect(() => {
      if (this.sideMenuService.isOpen()) {
        this.drawerVisible.set(true);
      } else {
        setTimeout(() => this.drawerVisible.set(false), 250); // 250ms = duración animación salida
      }
    });
  }

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth = auth;
    });
  }

  navigateTo(route: string): void {
    this.router.navigate([route]).then(() => {
      if (this.sideMenuService.isDrawer()) {
        this.sideMenuService.close(); 
      }
    });
  }

  isActive(item: any) {
    return this.router.url.includes(item.routerLink);
  }

  logout(): void {
    this.authService.logout()
      .subscribe({
        next: (response) => {
          this.messageService.showMessage('info', 'Has cerrado sesión correctamente', 5)
          this.router.navigate(['/catalog'])
        },
        error: (error) => {
          this.messageService.showMessage('error', 'Ha ocurrido un error. Inténtalo de nuevo...')
          console.error(error);
        },
        complete: () => {
        }
      });
  }
}
