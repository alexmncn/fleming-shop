import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { NavBarComponent } from "../../shared/nav-bar/nav-bar.component";
import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";

@Component({
    selector: 'app-catalog',
    imports: [RouterOutlet, NavBarComponent, FloatingMessageComponent],
    templateUrl: './catalog.component.html',
    styleUrl: './catalog.component.css'
})
export class CatalogComponent {

}
