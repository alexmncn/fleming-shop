import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink } from '@angular/router';
import { MatDivider } from '@angular/material/divider';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, MatDivider],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css'
})
export class AuthComponent {
  loginActive: boolean = true;
  registerActive: boolean = false;

  changeActive(select: string): void {
    if (select == 'login') {
      this.loginActive = true;
      this.registerActive = false;
    } else if (select == 'register') {
      this.loginActive = false;
      this.registerActive = true;
    }
  }
}