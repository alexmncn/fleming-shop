import { Component, ViewChild } from '@angular/core';

import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { trigger, style, transition, animate, state } from '@angular/animations';
import { NgxTurnstileModule } from 'ngx-turnstile';
import { NgxTurnstileComponent } from 'ngx-turnstile';

import { AuthService } from '../../../services/auth/auth.service';
import { MessageService } from '../../../services/message/message.service';

import { environment } from '../../../../environments/environment';

@Component({
    selector: 'app-register',
    imports: [ReactiveFormsModule, NgxTurnstileModule],
    templateUrl: './register.component.html',
    styleUrl: './register.component.css',
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
export class RegisterComponent {
  registerForm: FormGroup;
  otpForm: FormGroup;
  
  passwordMinLen: number = 4;
  passwordMatch: boolean = true;
  credentialsError: boolean = false;

  tempUsername: string = '';
  tempPassword: string = '';

  OTPlength = 6

  registerStep = 0;

  defaultRedirectRoute: string = '/auth/login'

  // Turnstile captcha
  @ViewChild('turnstileRef') turnstileComponent!: NgxTurnstileComponent;
  turnstileSiteKey: string = environment.turnstileSiteKey;
  turnstileResolved: boolean = false;
  turnstileResponse: string | null = null;

  isLoading: boolean = false;


  constructor(private messageService: MessageService, private authService: AuthService, private router: Router, private fb: FormBuilder) { 
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(this.passwordMinLen)]],
      confirm_password: ['', Validators.required]
    });

    this.otpForm = this.fb.group({
      OTPcode: ['', Validators.required]
    });
  }

  sendRegister() {
    if (this.registerStep == 0) {
      if (this.registerForm.valid && this.turnstileResolved) {
        if (this.registerForm.value.password == this.registerForm.value.confirm_password) {
            this.isLoading = true;

            this.authService.register(this.registerForm.value.username, this.registerForm.value.password, this.turnstileResponse, null)
            .subscribe({
              error: (error) => {
                if (error.status == 303) {
                  this.registerStep = 1;
                  this.tempUsername = this.registerForm.value.username;
                  this.tempPassword = this.registerForm.value.password;
                  this.messageService.showMessage('warn', 'Necesitas el código de confirmación para completar el registro', 0);
                } else if (error.status == 400) {
                  this.messageService.showMessage('error', 'Error en el captcha. Inténtalo de nuevo en unos segundos...');
                } else if (error.status == 409) {
                  this.credentialsError = true;
                  this.messageService.showMessage('error', 'El usuario ya existe. Inténtalo de nuevo...');
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
          this.passwordMatch = false;
          this.messageService.showMessage('error', 'Las contraseñas no coinciden');
        } 
      } else {
        if (!this.turnstileResolved) {
          this.messageService.showMessage('warn', 'Debes completar el captcha');
        } else {
          this.messageService.showMessage('error', 'Los datos introducidos no son válidos');
          document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
        }
      }

    } else if (this.registerStep == 1) {
      if (this.registerForm.valid) {
        this.isLoading = true;

        this.authService.register(this.tempUsername, this.tempPassword, null, this.otpForm.value.OTPcode)
        .subscribe({
          next: (response) => {
            this.messageService.showMessage('success', 'Registro exitoso', 5);

            // redirect
            const redirectUrl = this.authService.redirectUrl || this.defaultRedirectRoute;
            this.router.navigate([redirectUrl]);
          },
          error: (error) => {
            if (error.status == 409) {
              this.credentialsError = true;
              this.messageService.showMessage('error', 'El usuario ya existe. Inténtalo de nuevo');
            } else if (error.status == 422) {
              this.messageService.showMessage('error', 'El código introducido no es válido');
            } else if (error.status == 410) {
              this.messageService.showMessage('error', 'El código ha expirado. Inténtalo de nuevo');
            } else if (error.status == 0 || error.status == 500) {
              this.messageService.showMessage('error', 'Error del servidor. Inténtalo de nuevo más tarde');
            }
            this.isLoading = false;
          }
        });
      } else {
        document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
        this.messageService.showMessage('error', 'Los datos introducidos no son válidos');
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

