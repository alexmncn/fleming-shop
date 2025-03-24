import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIcon } from '@angular/material/icon';

import { AuthService } from '../../services/auth/auth.service';

@Component({
    selector: 'app-header',
    imports: [RouterLink, CommonModule, MatIcon],
    templateUrl: './header.component.html',
    styleUrl: './header.component.css'
})
export class HeaderComponent implements OnInit {
  isAuth: boolean = false;
  username: string | null = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.isAuthenticated$.subscribe((auth: boolean) => {
      this.isAuth = auth;
    });

    this.authService.username$.subscribe((name: string | null) => {
      this.username = name;
    });
    
  }
}