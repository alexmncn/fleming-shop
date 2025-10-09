import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';

import { HeaderComponent } from './shared/header/header.component';
import { FooterComponent } from "./shared/footer/footer.component";
import { SideMenuComponent } from './shared/side-menu/side-menu.component';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, HeaderComponent, FooterComponent, SideMenuComponent],
    templateUrl: './app.component.html',
    styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'Fleming Shop';

  constructor(private router: Router) {}

  get showFooter(): boolean {
    return this.atCatalog || this.atAuth;
  }

  get atCatalog(): boolean {
    return this.router.url.startsWith('/catalog/');
  }

  get atAuth(): boolean {
    return this.router.url.startsWith('/auth/');
  }
}
