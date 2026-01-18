import { Component, Input, OnDestroy, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { trigger, style, transition, animate, sequence } from '@angular/animations';

import { MessageService, Message } from '../../services/message/message.service';

@Component({
    selector: 'app-floating-message',
    imports: [CommonModule],
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
                ])
            ])
        ])
    ]
})
export class FloatingMessageComponent implements OnInit {
    messages: Message[] = [];
    isHidden = signal(true); // Inicialmente oculto
    private hideTimeout: any = null;
    
    // Duración de la animación de salida (200ms)
    private readonly LEAVE_ANIMATION_DURATION = 200;
    
    constructor(private messageService: MessageService) { }
  
    ngOnInit(): void {
      this.messageService.currentMessages.subscribe((msgs) => {
        this.messages = msgs;
        this.updateVisibility(msgs);
      });
    }
  
    private updateVisibility(msgs: Message[]): void {
      // Cancelar timeout anterior si existe
      if (this.hideTimeout) {
        clearTimeout(this.hideTimeout);
        this.hideTimeout = null;
      }

      if (msgs.length === 0) {
        // Si no hay mensajes, esperar a que termine la animación antes de ocultar
        this.hideTimeout = setTimeout(() => {
          this.isHidden.set(true);
          this.hideTimeout = null;
        }, this.LEAVE_ANIMATION_DURATION);
      } else {
        // Si hay mensajes, mostrar inmediatamente
        this.isHidden.set(false);
      }
    }
  
    // Método para cerrar un mensaje manualmente
    closeMessage(id: number): void {
      this.messageService.removeMessage(id);
    }    
}
