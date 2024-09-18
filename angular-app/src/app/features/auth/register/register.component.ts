import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { Router } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { trigger, style, transition, animate } from '@angular/animations';

import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [RouterOutlet, CommonModule, ReactiveFormsModule],
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
    ])
  ]
})
export class RegisterComponent {
  registerForm: FormGroup;

  passwordMinLen: number = 4;
  password_match: boolean = true;
  credentialsError: boolean = false;

  defaultRedirectRoute: string = 'login'

  // loading overlay
  isLoading: boolean = false;
  loadingInfo: string = '';


  constructor(private authService: AuthService, private router: Router, private fb: FormBuilder) { 
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(this.passwordMinLen)]],
      confirm_password: ['', Validators.required]
    });
  }

  sendRegister() {
    if (this.registerForm.valid) {
      if (this.registerForm.value.password == this.registerForm.value.confirm_password) {
        this.isLoading = true;
        this.loadingInfo = 'Enviando...';
        
        this.authService.register(this.registerForm.value.username, this.registerForm.value.password)
          .subscribe({
            next: (response) => {
              this.loadingInfo = 'Procesando...';
              setTimeout(() => {
                // redirect
                const redirectUrl = this.authService.redirectUrl || this.defaultRedirectRoute;
                this.router.navigate([redirectUrl]);
              }, 1000);    
            },
            error: (error) => {
              if (error.status == 409) {
                //this.messageService.showMessage('error', 'Este usuario ya existe');
                this.credentialsError = true;
              } else if (error.status == 0 || error.status == 500) {
                //this.messageService.showMessage('error', 'Error del servidor. Inténtalo de nuevo mas tarde...');
              }
              this.isLoading = false;
            }
          });
      } else {
        //this.messageService.showMessage('error','Las contraseñas deben coincidir');
        this.password_match = false;
      }

    } else {
      //this.messageService.showMessage('error','Los datos introducidos no son válidos');
      document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
    }
  }
}

