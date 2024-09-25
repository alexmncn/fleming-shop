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
  otpForm: FormGroup;
  
  passwordMinLen: number = 4;
  passwordMatch: boolean = true;
  credentialsError: boolean = false;

  tempUsername: string = '';
  tempPassword: string = '';

  OTPlength = 6

  registerStep = 0;

  defaultRedirectRoute: string = '/auth/login'

  isLoading: boolean = false;


  constructor(private authService: AuthService, private router: Router, private fb: FormBuilder) { 
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
      if (this.registerForm.valid) {
        if (this.registerForm.value.password == this.registerForm.value.confirm_password) {
            this.isLoading = true;

            this.authService.register(this.registerForm.value.username, this.registerForm.value.password)
            .subscribe({
              error: (error) => {
                if (error.status == 303) {
                  this.registerStep = 1;
                  this.tempUsername = this.registerForm.value.username;
                  this.tempPassword = this.registerForm.value.password;
                  console.log(error.error.message)
                } else if (error.status == 409) {
                  this.credentialsError = true;
                  console.log(error.error.message)
                } else if (error.status == 0 || error.status == 500) {
                  console.log(error.error.message)
                }
                this.isLoading = false;
              }
            });
        } else {
          this.passwordMatch = false;
          console.log('password doesnt match')
        } 
      } else {
        document.querySelectorAll('input').forEach(input => { input.classList.add('error');})
      }

    } else if (this.registerStep == 1) {
      console.log('OTP STEP SEND')
      if (this.registerForm.valid) {
        this.isLoading = true;

        this.authService.register(this.tempUsername, this.tempPassword, this.otpForm.value.OTPcode)
        .subscribe({
          next: (response) => {
              console.log(response.message)

            setTimeout(() => {
              // redirect
              const redirectUrl = this.authService.redirectUrl || this.defaultRedirectRoute;
              this.router.navigate([redirectUrl]);
            }, 1000);
          },
          error: (error) => {
            if (error.status == 409) {
              this.credentialsError = true;
              console.log(error.error.message)
            } else if (error.status == 422) {
              console.log(error.error.message)
            } else if (error.status == 410) {
              console.log(error.error.message)
            } else if (error.status == 0 || error.status == 500) {
              console.log(error.error.message)
            }
            this.isLoading = false;
          }
        });
      }
    }
  }
}

