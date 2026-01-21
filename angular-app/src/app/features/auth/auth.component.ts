import { Component, OnInit } from '@angular/core';

import { Router, RouterOutlet, RouterLink } from '@angular/router';
import { MatIcon } from '@angular/material/icon';
import { MatDivider } from '@angular/material/divider';
import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";

@Component({
    selector: 'app-auth',
    imports: [RouterOutlet, RouterLink, MatDivider, MatIcon, FloatingMessageComponent],
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