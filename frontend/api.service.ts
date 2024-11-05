import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000'; // Assuming Flask runs on port 5000
  private tokenSubject: BehaviorSubject<string | null>;
  public token: Observable<string | null>;

  constructor(private http: HttpClient) {
    this.tokenSubject = new BehaviorSubject<string | null>(localStorage.getItem('token'));
    this.token = this.tokenSubject.asObservable();
  }

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
    return this.http.post<any>(`${this.apiUrl}/login`, { username, password, jobTitle })
      .pipe(
        tap(response => {
          console.log('Login successful', response);
          localStorage.setItem('token', response.access_token);
          localStorage.setItem('jobTitle', response.job_title);
          this.tokenSubject.next(response.access_token);
        }),
        catchError(this.handleError)
      );
  }

  startInterview(page: number = 1, perPage: number = 10): Observable<any> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get(`${this.apiUrl}/interview`, { headers: this.authHeader(), params })
      .pipe(
        tap(response => console.log('Interview started', response)),
        catchError(this.handleError)
      );
  }

  sendMessage(message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/interview`, { message }, { headers: this.authHeader() })
      .pipe(
        tap(response => console.log('Message sent', response)),
        catchError(this.handleError)
      );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/logout`, {}, { headers: this.authHeader() })
      .pipe(
        tap(response => {
          console.log('Logout successful', response);
          localStorage.removeItem('token');
          localStorage.removeItem('jobTitle');
          this.tokenSubject.next(null);
        }),
        catchError(this.handleError)
      );
  }

  isLoggedIn(): boolean {
    return !!this.tokenSubject.value;
  }

  private authHeader() {
    const token = this.tokenSubject.value;
    if (token) {
      return new HttpHeaders().set('Authorization', `Bearer ${token}`);
    }
    return new HttpHeaders();
  }
}