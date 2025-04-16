import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIcon } from '@angular/material/icon';
import { trigger, style, transition, animate, sequence } from '@angular/animations';

import { MessageService } from '../../services/message/message.service';

@Component({
    selector: 'app-floating-message',
    imports: [CommonModule, MatIcon],
    templateUrl: './floating-message.component.html',
    styleUrl: './floating-message.component.css',
    animations: [
        trigger('slideInRight', [
            transition(':enter', [
                style({ height: '0px', opacity: 0, transform: 'translateX(-100%)' }),
                sequence([
                    animate('200ms ease-out', style({ height: '*' })),
                    animate('300ms ease-out', style({ transform: 'translateX(0)', opacity: 1 }))
                ])
            ]),
            transition(':leave', [
                sequence([
                    animate('200ms ease-in', style({ transform: 'translateX(100%)', opacity: 0 })),
                    animate('200ms ease-in', style({ height: '0px' }))
                ])
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
