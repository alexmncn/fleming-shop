import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { AuthService } from './auth.service';
import { MessageService } from '../message/message.service';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const messageService = inject(MessageService); // Inyección de dependencia con inject
  const router = inject(Router);
  
  const authToken = authService.getToken();

  // Clone req and add header
  const authReq = authToken
    ? req.clone({
        headers: req.headers.set('Authorization', `Bearer ${authToken}`),
      })
    : req;


    return next(authReq).pipe(
      catchError((error) => {
        if (error.status === 401) {
          // Delete token
          authService.clearToken();
          localStorage.clear();
          
          messageService.showMessage('warn', 'No tienes permiso para entrar a esta página', 5);

          // Redirect login
          router.navigate(['/auth']);
        }
  
        return throwError(() => error);
      })
    );
  };