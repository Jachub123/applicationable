import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ServiceService {
  private apiUrl = 'http://127.0.0.1:5050';

  constructor(private http: HttpClient) { }

  getdata(): Observable<any> {
    return this.http.get(`${this.apiUrl}/`);
  }

  getUserData(username: string): Observable<any> {
    const params = new HttpParams().set('username', username);
    return this.http.get(`${this.apiUrl}/user_data`, { params });
  }

  addEntry(username: string, entry: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/add`, { username, entry });
  }
}
