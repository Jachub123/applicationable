import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ServiceService } from './services/service.service';
import { LocalStorageService } from './services/local-storage-service.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  newdata: any;
  chat: any = this.lss.getItem('chat');
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
  constructor(
    private _apiservice: ServiceService,
    private http: HttpClient,
    private lss: LocalStorageService
  ) {}
  ngOnInit(): void {
    console.log("this.lss.getItem('loggedIn')");
    console.log(this.lss.getItem('loggedIn'));
    console.log('showChat');
    console.log(this.showChat);
  }

  register(username: string, password: string, job: string) {
    this.http
      .post<any>('http://127.0.0.1:5000/api/login', {
        username: username,
        password: password,
        jobTitle: job,
      })
      .subscribe((data) => {
        this.lss.setItem('chat', JSON.stringify(data));
        this.lss.setItem('currentQuestion', data.current_question);
        this.retriveLocalStorage();

        if (this.currentQuestion) {
          this.lss.setItem('loggedIn', 'true');
          this.retriveLocalStorage();
        }
        console.log(data);
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
    console.log(this.lss.getItem('loggedIn'));
  }
  logout() {
    this.lss.clear();
    this.retriveLocalStorage();
  }

  sendMsg(msg: string) {
    console.log(this.chat);
    var chatObj = JSON.parse(this.chat);
    console.log(chatObj);

    this.http
      .post<any>('http://127.0.0.1:5000/api/interview', { message: msg })
      .subscribe((data) => {
        this.lss.setItem('chat', data);
        this.lss.setItem('currentQuestion', data.current_question);
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
