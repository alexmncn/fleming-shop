import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CookieService } from 'ngx-cookie-service';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private registerUrl = environment.apiUrl + '/register';
  private loginUrl = environment.apiUrl + '/login';
  private logoutUrl = environment.apiUrl + '/logout';
  private authUrl = environment.apiUrl + '/auth';

  public redirectUrl: string | null = null;
  public username: string = '';

  // Observable auth status for components
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.isAuthenticated());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  // Observable username for components
  private usernameSubject = new BehaviorSubject<string | null>(this.getUsername());
  public username$ = this.usernameSubject.asObservable();


  constructor(private http: HttpClient, private cookieService: CookieService) { }


  register(username: string, password: string, OTPcode: string = ''): Observable<any> {
    return OTPcode === '' 
      ? this.http.post<any>(this.registerUrl, { username, password }) 
      : this.http.post<any>(this.registerUrl, { username, password, OTPcode });
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(this.loginUrl, { username, password }).pipe(
      tap((response: any) => {
        this.storeToken(response.token, response.expires_at);
        this.setUsername(username);
        this.isAuthenticatedSubject.next(true);
        this.usernameSubject.next(username);
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post<any>(this.logoutUrl, {}).pipe(
      tap((response: any) => {
        this.clearToken();
        localStorage.clear();
      })
    );
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token;
  }

  storeToken(token: string, expiresAt: string): void {
    const expireDate = new Date(expiresAt);
    this.cookieService.set('authToken', token, expireDate, '/', undefined, true, 'Strict');
  }

  getToken(): string | null {
    return this.cookieService.get('authToken');
  }

  clearToken(): void {
    this.cookieService.delete('authToken');
    this.isAuthenticatedSubject.next(false);
  }

  setUsername(username: string): void {
    localStorage.setItem('username', username);
  }

  getUsername(): string | null {
    return localStorage.getItem('username');
  }
}
