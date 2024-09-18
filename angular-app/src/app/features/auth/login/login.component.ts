import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { trigger, style, transition, animate } from '@angular/animations';

import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterOutlet, CommonModule, ReactiveFormsModule],
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
    ])
  ]
})
export class LoginComponent {
  loginForm: FormGroup;
  passwordMinLen: number = 4;
  credentialsError: boolean = false;

  defaultRedirectRoute: string = '/home';

  // loading overlay
  isLoading: boolean = false;
  loadingInfo: string = '';



  constructor(private authService: AuthService, private router: Router, private fb: FormBuilder) { 
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(this.passwordMinLen)]]
    });
  }

  sendLogin() {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.loadingInfo = 'Enviando...';

      this.authService.login(this.loginForm.value.username, this.loginForm.value.password)
        .subscribe({
          next: (response) => {
            this.loadingInfo = 'Procesando...';
              // Save the token with AuthService
              this.authService.storeToken(response.token, response.expires_at);
              this.authService.setUsername(response.username);
              setTimeout(() => {
              // Show success message
              //this.messageService.showMessage('success', 'Has iniciado sesión');

              // Close loading overlay
              this.isLoading = false;
              
              // Redirect
              const redirectUrl = this.authService.redirectUrl || this.defaultRedirectRoute;
              this.router.navigate([redirectUrl]);
              }, 1000);
          },
          error: (error) => {
            if (error.status == 401) {
              //this.messageService.showMessage('error', 'Credenciales incorrectas');
              this.credentialsError = true;
            } else if (error.status == 0 || error.status == 500) {
              //this.messageService.showMessage('error', 'Error del servidor. Inténtalo de nuevo mas tarde...');
            }

            this.isLoading = false;
          }
        });
    } else {
      //this.messageService.showMessage('error', 'Los datos introducidos no son válidos');
      document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
    }
  }
}
