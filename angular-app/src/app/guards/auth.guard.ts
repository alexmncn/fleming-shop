import { CanActivateFn } from '@angular/router';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const isAuth = authService.isAuthenticated();

  const isLoginOrRegisterRoute = state.url === '/auth/login' || state.url === '/auth/register';

  if (isAuth && isLoginOrRegisterRoute) {
    router.navigate(['/catalog/']);
    return false;
  }

  if (!isAuth && !isLoginOrRegisterRoute) {
    authService.redirectUrl = state.url;
    router.navigate(['/login']);
    return false;
  } else {
    return true;
  }
};
