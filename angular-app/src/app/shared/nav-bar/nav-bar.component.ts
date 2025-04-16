import { Component, HostListener } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { Router, RouterLink,  NavigationEnd } from '@angular/router';
import { trigger, style, transition, animate, sequence } from '@angular/animations';
import { MatIcon } from '@angular/material/icon';

import { SearchBarComponent } from "../search-bar/search-bar.component";

@Component({
    selector: 'app-nav-bar',
    imports: [CommonModule, RouterLink, MatIcon, SearchBarComponent],
    templateUrl: './nav-bar.component.html',
    styleUrl: './nav-bar.component.css',
    animations: [
      trigger('buttonIn', [
        // ENTRADA
        transition(':enter', [
          style({ width: '0px', transform: 'translateX(-50%)', opacity: 0 }),
          sequence([
            animate('200ms ease-out', style({ width: '*' })), // Expandir ancho
            animate('200ms ease-out', style({ transform: 'translateX(0%)', opacity: 1 })) // Deslizar y aparecer
          ])
        ]),
    
        // SALIDA
        transition(':leave', [
          sequence([
            animate('200ms ease-in', style({ transform: 'translateX(-50%)', opacity: 0 })), // Deslizar hacia fuera
            animate('200ms ease-in', style({ width: '0px' })) // Colapsar ancho
          ])
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
    return this.currentRoute === '/catalog/home';
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
