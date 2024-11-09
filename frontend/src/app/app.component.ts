import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LocalStorageService } from './services/local-storage-service.service';
import { catchError, map, Observable, of } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  newdata: any;
  chat: any;
  currentQuestion: any =
    this.lss.getItem('currentQuestion') === null || undefined
      ? undefined
      : this.lss.getItem('loggedIn');
  showChat: any =
    this.lss.getItem('loggedIn') === null || undefined
      ? 'false'
      : this.lss.getItem('loggedIn');

  pass: string = '';
  name: string = '';
  job: string = '';
  test: boolean = true;
  showWarn: string = '';
  showSuccess: string = '';

  constructor(private http: HttpClient, private lss: LocalStorageService) {}

  ngOnInit(): void {
    console.log(this.lss?.getItem('chat'));
    this.updateChat();
  }

  updateChat() {
    this.chat = JSON.parse(
      this.lss.getItem('chat') !== 'undefined'
        ? <string>this.lss.getItem('chat')
        : '{}'
    );
  }

  register(username: string, password: string, job: string) {
    this.http
      .post<any>(
        'http://127.0.0.1:5000/api/login',
        {
          username: username,
          password: password,
          jobTitle: job,
        },

        { observe: 'response', withCredentials: true }
      )
      .pipe(
        map((response) => {
          if (response.status === 200) {
            this.lss.setItem('loggedIn', 'true');
            this.retriveLocalStorage();
          }
        }),
        catchError((error: any): Observable<any> => {
          if (error) {
            this.showWarn = error.error.error;
          }
          // after handling error, return a new observable
          // that doesn't emit any values and completes
          return of();
        })
      )
      .subscribe((data) => {
        console.log(JSON.stringify(data));
        this.lss.setItem('chat', JSON.stringify(data));
        this.retriveLocalStorage();
      });
  }
  retriveLocalStorage() {
    this.currentQuestion =
      this.lss.getItem('currentQuestion') === null || undefined
        ? null
        : this.lss.getItem('currentQuestion');
    this.showChat =
      this.lss.getItem('loggedIn') === null || undefined
        ? 'false'
        : this.lss.getItem('loggedIn');
    this.showWarn = '';
    this.showSuccess = '';
  }
  logout() {
    this.http
      .post<any>(
        'http://127.0.0.1:5000/api/logout',
        {},
        { withCredentials: true }
      )
      .subscribe((response) => {
        this.lss.clear();
        this.updateChat();
        this.retriveLocalStorage();
        this.showSuccess = response.message;
      });
  }

  sendMsg(msg: string) {
    this.http
      .post<any>(
        'http://127.0.0.1:5000/api/interview',
        { message: msg },
        { withCredentials: true }
      )
      .pipe(
        catchError((error: any): Observable<any> => {
          if (error) {
            if (error.status === 401) {
              this.lss.setItem('loggedIn', 'false');
              this.retriveLocalStorage();
              this.showWarn = error.error.error;
            }
          }
          // after handling error, return a new observable
          // that doesn't emit any values and completes
          return of();
        })
      )
      .subscribe((data) => {
        console.log(JSON.stringify(data));
        this.lss.setItem('chat', JSON.stringify(data));
        this.lss.setItem('currentQuestion', data.current_question);
        this.updateChat();
        if (this.currentQuestion) {
          this.lss.setItem('loggedIn', 'true');
          this.retriveLocalStorage();
        }
        console.log(data);
      });
  }
  /*   getData() {
    this._apiservice.getdata().subscribe((res: any) => {
      this.newdata = res;
      console.log(res.current_question);
      if (res.current_question) {
        this.showChat = true;
      }
    });
  } */
}
