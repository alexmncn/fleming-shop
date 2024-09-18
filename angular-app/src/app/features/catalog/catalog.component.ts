import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { NavBarComponent } from "../../shared/nav-bar/nav-bar.component";

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [RouterOutlet, NavBarComponent],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.css'
})
export class CatalogComponent {

}
