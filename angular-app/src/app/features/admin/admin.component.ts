import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth/auth.service';
import { MessageService } from '../../services/message/message.service';

@Component({
    selector: 'app-admin',
    imports: [],
    templateUrl: './admin.component.html',
    styleUrl: './admin.component.css'
})
export class AdminComponent {


  constructor(private authService: AuthService, private router: Router, private messageService: MessageService) {}

  logout(): void {
    this.authService.logout()
      .subscribe({
        next: (response) => {
          this.messageService.showMessage('info', 'Has cerrado sesión correctamente')
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
