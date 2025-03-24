import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIcon } from '@angular/material/icon';
import { trigger, style, transition, animate, state } from '@angular/animations';

import { MessageService } from '../../services/message/message.service';

@Component({
    selector: 'app-floating-message',
    imports: [CommonModule, MatIcon],
    templateUrl: './floating-message.component.html',
    styleUrl: './floating-message.component.css',
    animations: [
        trigger('slideInDown', [
            state('void', style({
                transform: 'translateY(-100%)',
                opacity: 0
            })),
            transition(':enter', [
                animate('0.5s ease-out', style({
                    transform: 'translateY(0)',
                    opacity: 1
                }))
            ]),
            transition(':leave', [
                animate('0.3s ease-in', style({
                    transform: 'translateY(-100%)',
                    opacity: 0
                }))
            ])
        ])
    ]
})
export class FloatingMessageComponent {
  message: { type: string, text: string } = { type: '', text: '' };

  constructor(private messageService: MessageService) {}

  ngOnInit(): void {
    this.messageService.currentMessage.subscribe(message => this.message = message);
  }

  closeMessage() {
    this.messageService.clearMessage();
  }
}
