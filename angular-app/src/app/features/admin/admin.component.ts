import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { RouterOutlet } from '@angular/router';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';
import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";

@Component({
    selector: 'app-admin',
    imports: [RouterOutlet, RouterLink, CommonModule, FloatingMessageComponent],
    templateUrl: './admin.component.html',
    styleUrl: './admin.component.css'
})
export class AdminComponent {
  expanded = true;

  menuItems = [
    { label: 'Catálogo', icon: 'pi pi-home', routerLink: '/catalog/home' },
    { label: 'Ventas', icon: 'pi pi-dollar', routerLink: '/admin/sales' },
    { label: 'Exportar datos', icon: 'pi pi-file-export', routerLink: '/admin/data-export' },
  ];

  constructor(private authService: AuthService, private router: Router, private messageService: MessageService) {}

  toggleDrawer() {
    this.expanded = !this.expanded;
  }

  isActive(item: any) {
    return this.router.url === item.routerLink;
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
