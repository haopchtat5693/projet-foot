import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap, of } from 'rxjs';
import { TokenResponse } from '../interfaces/token';

const TOKEN_KEY = 'projet-foot.auth-token';
declare const APP_API_URL: string;

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = APP_API_URL;

  private readonly tokenState = signal<string | null>(this.readToken());

  readonly token = this.tokenState.asReadonly();
  readonly isAuthenticated = computed(() => this.token() !== null);

  login(username: string, password: string): Observable<TokenResponse> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http.post<TokenResponse>(`${this.apiUrl}/login/`, body.toString(), { headers }).pipe(
      tap((response) => {
        this.tokenState.set(response.access_token);
        window.localStorage.setItem(TOKEN_KEY, response.access_token);
      })
    );
  }

  register(username: string, password: string): Observable<unknown> {
    return this.http.post<unknown>(`${this.apiUrl}/users/`, {
      username,
      password,
    });
  }

  logout(): Observable<unknown> {
    const currentToken = this.token();

    this.tokenState.set(null);
    window.localStorage.removeItem(TOKEN_KEY);

    if (!currentToken) {
      return of(null);
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${currentToken}`,
    });

    return this.http.post<unknown>(`${this.apiUrl}/logout/`, {}, { headers });
  }

  private readToken(): string | null {
    try {
      return window.localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  }
}