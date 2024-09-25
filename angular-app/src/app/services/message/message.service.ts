import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  defaultDuration: number = 10;

  private messageSource = new BehaviorSubject<{type: string, text: string}>({type: '', text: ''});
  currentMessage = this.messageSource.asObservable();

  constructor() { }

  showMessage(type: string, text: string, duration: number = this.defaultDuration) {
    this.messageSource.next({ type, text });
    
    if (duration > 0) {
      setTimeout(() => {
        this.clearMessage();
      }, duration * 1000); // seconds to miliseconds
    }
  }

  clearMessage() {
    this.messageSource.next({type: '', text: ''});
  }
}
