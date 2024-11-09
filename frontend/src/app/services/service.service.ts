import { HttpClient, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ServiceService {
  constructor(private _http: HttpClient) {}
  getdata(): Observable<HttpResponse<Object>> {
    return this._http.get('http://localhost:5000/api/interview', {
      observe: 'response',
    });
  }
}
