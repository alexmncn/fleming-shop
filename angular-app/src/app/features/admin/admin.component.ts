import { Component } from '@angular/core';

import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [],
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent {

  constructor(private authService: AuthService) {}

  logout(): void {
    this.authService.logoutReq()
      .subscribe({
        next: (response) => {
          console.log(response);
          this.authService.logout();
          window.location.reload();
        },
        error: (error) => {
          console.error(error);
        },
        complete: () => {
        }
      });

  }
}
