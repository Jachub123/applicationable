import { Component, OnInit } from '@angular/core';
import { ServiceService } from './service.service';
import { SessionService } from './session.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  username: string = '';
  password: string = '';
  loginError: string = '';
  isLoggedIn: boolean = false;
  userData: any = null;
  newEntry: string = '';

  constructor(
    private serviceService: ServiceService,
    private sessionService: SessionService,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkSession();
  }

  checkSession() {
    if (this.sessionService.isLoggedIn()) {
      const session = this.sessionService.getSession();
      this.isLoggedIn = true;
      this.username = session.username;
      this.fetchUserData();
    } else {
      this.isLoggedIn = false;
      this.userData = null;
    }
  }

  login() {
    this.loginError = '';
    this.serviceService.getdata().subscribe(
      (data) => {
        if (data.message === "Welcome to the home page") {
          this.sessionService.setSession(this.username);
          this.isLoggedIn = true;
          this.fetchUserData();
        } else {
          this.loginError = 'Login failed. Please check your credentials.';
        }
      },
      (error) => {
        console.error('Error during login:', error);
        this.loginError = 'An error occurred during login. Please try again later.';
      }
    );
  }

  logout() {
    this.sessionService.clearSession();
    this.isLoggedIn = false;
    this.userData = null;
    this.username = '';
    this.password = '';
  }

  fetchUserData() {
    this.serviceService.getUserData(this.username).subscribe(
      (data) => {
        this.userData = data;
      },
      (error) => {
        console.error('Error fetching user data:', error);
      }
    );
  }

  addEntry() {
    if (this.newEntry.trim()) {
      this.serviceService.addEntry(this.username, this.newEntry).subscribe(
        (response) => {
          if (response.success) {
            this.fetchUserData(); // Refresh user data after adding entry
            this.newEntry = ''; // Clear the input field
          } else {
            console.error('Failed to add entry:', response.message);
          }
        },
        (error) => {
          console.error('Error adding entry:', error);
        }
      );
    }
  }
}
