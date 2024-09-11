import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ServiceService } from './service.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  newdata: any;
  postId: any;
  pass: string = '';
  name: string = '';
  constructor(private _apiservice: ServiceService, private http: HttpClient) {}

  ngOnInit() {
    this.getData();
  }
  register(username: string, password: string) {
    this.http
      .post<any>('http://127.0.0.1:5050/login', {
        user: username,
        pass: password,
      })
      .subscribe((data) => {
        this.postId = data.id;
      });
  }
  getData() {
    this._apiservice.getdata().subscribe((res) => {
      this.newdata = res;
      console.log(res);
    });
  }
}
