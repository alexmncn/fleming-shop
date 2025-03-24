import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, RouterLink } from '@angular/router';
import { MatDivider } from '@angular/material/divider';

@Component({
    selector: 'app-auth',
    imports: [CommonModule, RouterOutlet, RouterLink, MatDivider],
    templateUrl: './auth.component.html',
    styleUrl: './auth.component.css'
})
export class AuthComponent implements OnInit{
  loginActive: boolean = true;
  registerActive: boolean = false;

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.changeActive()
  }

  changeActive(select: string = ''): void {
    if (select == 'login') {
      this.loginActive = true;
      this.registerActive = false;
    } else if (select == 'register') {
      this.loginActive = false;
      this.registerActive = true;
    } else {
      if (this.router.url == '/auth/login') {
        this.loginActive = true;
        this.registerActive = false;
      } else if (this.router.url == '/auth/register') {
        this.loginActive = false;
        this.registerActive = true;
      }
    }
  }
}