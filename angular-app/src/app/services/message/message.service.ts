import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface Message {
  id: number;
  type: string;
  text: string;
  duration: number;
}

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  defaultDuration: number = 10;
  private nextId = 1;
  private messages: Message[] = [];
  private messagesSource = new BehaviorSubject<Message[]>([]);
  
  // El observable que se suscribirá el componente.
  currentMessages = this.messagesSource.asObservable();

  constructor() { }

  // Agrega un mensaje a la lista
  showMessage(type: string, text: string, duration: number = this.defaultDuration) {
    // Buscar y eliminar mensajes existentes con el mismo texto
    const existingMessages = this.messages.filter(message => message.text === text);
    existingMessages.forEach(message => {
      this.removeMessage(message.id);
    });

    // Añadir el nuevo mensaje
    const id = this.nextId++;
    const newMessage: Message = { id, type, text, duration };
    this.messages.push(newMessage);
    this.messagesSource.next(this.messages);

    // Si la duración es mayor a 0, programar eliminar el mensaje luego de esa duración
    if (duration > 0) {
      setTimeout(() => {
        this.removeMessage(id);
      }, duration * 1000);
    }
  }

  // Método para eliminar un mensaje individualmente
  removeMessage(id: number) {
    this.messages = this.messages.filter(message => message.id !== id);
    this.messagesSource.next(this.messages);
  }

  // Método para limpiar todos los mensajes
  clearMessages() {
    this.messages = [];
    this.messagesSource.next(this.messages);
  }
}
