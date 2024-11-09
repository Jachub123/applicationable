import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = `${environment.apiUrl}/api`;  // Add /api prefix

  constructor(private http: HttpClient) {}

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Error: ${error.error.message}`;
      console.error('Client side error:', error.error.message);
    } else {
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.error.error || error.message}`;
      console.error('Server side error:', error);
    }
    return throwError(errorMessage);
  }

  login(username: string, password: string, jobTitle: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login`, 
      { username, password, jobTitle }, 
      { withCredentials: true }  // Enable credentials
    ).pipe(
      tap(response => {
        console.log('Login successful', response);
        localStorage.setItem('jobTitle', response.job_title);
      }),
      catchError(this.handleError)
    );
  }

  startInterview(): Observable<any> {
    return this.http.get(`${this.apiUrl}/interview`, { 
      withCredentials: true  // Enable credentials
    }).pipe(
      tap(response => console.log('Interview started', response)),
      catchError(this.handleError)
    );
  }

  sendMessage(message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/interview`, 
      { message }, 
      { withCredentials: true }  // Enable credentials
    ).pipe(
      tap(response => console.log('Message sent', response)),
      catchError(this.handleError)
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/logout`, 
      {}, 
      { withCredentials: true }  // Enable credentials
    ).pipe(
      tap(response => {
        console.log('Logout successful', response);
        localStorage.removeItem('jobTitle');
      }),
      catchError(this.handleError)
    );
  }

  isLoggedIn(): boolean {
    // Since we're using session cookies, we'll rely on the backend to tell us
    // if we're logged in or not through the startInterview endpoint
    return true;
  }
}
