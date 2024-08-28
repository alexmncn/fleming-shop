import { Component, HostListener } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { Router, RouterLink,  NavigationEnd } from '@angular/router';
import { trigger, style, transition, animate, state } from '@angular/animations';
import { MatIcon } from '@angular/material/icon';

import { SearchBarComponent } from "../search-bar/search-bar.component";

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [ CommonModule, RouterLink, MatIcon, SearchBarComponent],
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.css',
  animations:[
    trigger('buttonOut', [
      state('void', style({
        transform: 'translateX(-50%)',
        opacity: 0
      })),
      transition(':enter', [
        animate('0.3s ease-out', style({
          transform: 'translateX(0%)',
          opacity: 1
        }))
      ]),
      transition(':leave', [
        animate('0.3s ease-out', style({
          transform: 'translateX(-50%)',
          opacity: 0
        }))
      ])
    ])
  ]
})
export class NavBarComponent {
  currentRoute: string = "";
  inputFocused: boolean = true;
  isScreenSmall: boolean = window.innerWidth <= 600;
  hideButtons: boolean = false;

  constructor(private router: Router, private location: Location) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.currentRoute = event.urlAfterRedirects;
      }
    });
  }

  goBack(): void {
    this.location.back();
  }

  get atHome(): boolean {
    return this.currentRoute === '/home';
  }

  isInputFocused(param: boolean = false): void {
    this.inputFocused = param;
    this.hideButtons = this.inputFocused && this.isScreenSmall;
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: Event) {
    this.isScreenSmall = window.innerWidth <= 600;
  }
}
