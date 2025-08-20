import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { RouterOutlet } from '@angular/router';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';
import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";

@Component({
    selector: 'app-admin',
    imports: [RouterOutlet, CommonModule, FloatingMessageComponent],
    templateUrl: './admin.component.html',
    styleUrl: './admin.component.css'
})
export class AdminComponent {
  expanded = true;

  menuItems = [
    { label: 'Dashboard', icon: 'pi pi-home' },
    { label: 'Usuarios', icon: 'pi pi-users' },
    { label: 'Ajustes', icon: 'pi pi-cog' }
  ];

  constructor(private authService: AuthService, private router: Router, private messageService: MessageService) {}

  toggleDrawer() {
    this.expanded = !this.expanded;
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
