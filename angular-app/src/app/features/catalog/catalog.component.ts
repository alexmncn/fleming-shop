import { Component } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';

import { NavBarComponent } from "../../shared/nav-bar/nav-bar.component";
import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";
import { filter } from 'rxjs';

@Component({
    selector: 'app-catalog',
    imports: [RouterOutlet, NavBarComponent, FloatingMessageComponent],
    templateUrl: './catalog.component.html',
    styleUrl: './catalog.component.css'
})
export class CatalogComponent {
    constructor(private router: Router) {
    this.router.events.pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
    .subscribe(() => {
        setTimeout(() => {
        const container = document.querySelector('.main-content');
        container?.scrollTo({ top: 0 });
        }, 0);
    });
  }
}
