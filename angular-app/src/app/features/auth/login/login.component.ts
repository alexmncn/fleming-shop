import { Component, ViewChild } from '@angular/core';

import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { NgxTurnstileModule } from 'ngx-turnstile';
import { NgxTurnstileComponent } from 'ngx-turnstile';

import { AuthService } from '../../../services/auth/auth.service';
import { MessageService } from '../../../services/message/message.service';

import { environment } from '../../../../environments/environment';

@Component({
    selector: 'app-login',
    imports: [ReactiveFormsModule, NgxTurnstileModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css',
    animations: [
        trigger('errorAnimation', [
            transition(':enter', [
                style({ opacity: 0 }),
                animate('150ms ease-in', style({ height: '*', opacity: 1 }))
            ]),
            transition(':leave', [
                animate('0ms ease-out', style({ height: '0', opacity: 0 }))
            ])
        ]),
        trigger('slideInDown', [
            state('void', style({
                transform: 'translateY(-25%)',
                opacity: 0
            })),
            transition(':enter', [
                animate('0.5s ease-out', style({
                    transform: 'translateY(0)',
                    opacity: 1
                }))
            ])
        ])
    ]
})
export class LoginComponent {
  loginForm: FormGroup;
  passwordMinLen: number = 4;
  credentialsError: boolean = false;

  defaultRedirectRoute: string = '/home';

  // Turnstile captcha
  @ViewChild('turnstileRef') turnstileComponent!: NgxTurnstileComponent;
  turnstileSiteKey: string = environment.turnstileSiteKey;
  turnstileResolved: boolean = false;
  turnstileResponse: string | null = null;

  isLoading: boolean = false;


  constructor(private messageService: MessageService, private authService: AuthService, private router: Router, private fb: FormBuilder) { 
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(this.passwordMinLen)]]
    });
  }

  sendLogin() {
    if (this.loginForm.valid && this.turnstileResolved) {
      this.isLoading = true;

      this.authService.login(this.loginForm.value.username, this.loginForm.value.password, this.turnstileResponse)
        .subscribe({
          next: (response) => {
            this.isLoading = false;

            this.messageService.showMessage('success', 'Has iniciado sesión', 5);
            
            // Redirect
            const redirectUrl = this.authService.redirectUrl || this.defaultRedirectRoute;
            this.router.navigate([redirectUrl]);
          },
          error: (error) => {
            if (error.status == 400) {
              this.messageService.showMessage('error', 'Error en el captcha. Inténtalo de nuevo en unos segundos...');
            } else if (error.status == 401) {
              this.messageService.showMessage('error', 'Credenciales incorrectas. Inténtalo de nuevo...');
              this.credentialsError = true;
            } else if (error.status == 0 || error.status == 500) {
              this.messageService.showMessage('error', 'Error del servidor. Inténtalo de nuevo más tarde...');
            }

            this.isLoading = false;

            // Reset turnstile captcha
            this.turnstileResolved = false;
            this.turnstileResponse = null;
            this.turnstileComponent.reset();
          }
        });
    } else {
      if (!this.turnstileResolved) {
        this.messageService.showMessage('warn', 'Debes completar el captcha');
      } else {
        this.messageService.showMessage('error', 'Los datos introducidos no son válidos');
        document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
      }
    }
  }

  handleTurnstileResolved(response: string | null): void {
    if (response) {
      this.turnstileResponse = response;
      this.turnstileResolved  = true;
    } else {
      this.turnstileResponse = null;
      this.turnstileResolved = false;
      console.log('Captcha no resuelto o inválido.');
    }
  }
}
