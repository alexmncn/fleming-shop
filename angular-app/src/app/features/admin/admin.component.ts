import { Component, signal, HostListener } from '@angular/core';


import { RouterOutlet } from '@angular/router';

import { FloatingMessageComponent } from "../../shared/floating-message/floating-message.component";

@Component({
    selector: 'app-admin',
    imports: [RouterOutlet, FloatingMessageComponent],
    templateUrl: './admin.component.html',
    styleUrl: './admin.component.css'
})
export class AdminComponent {
}
