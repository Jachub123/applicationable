import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container">
      <header>
        <h1>Interview Application</h1>
        <nav>
          <a routerLink="/login" *ngIf="!isLoggedIn">Login</a>
          <a routerLink="/interview" *ngIf="isLoggedIn">Interview</a>
          <a href="#" (click)="logout()" *ngIf="isLoggedIn">Logout</a>
        </nav>
      </header>
      <main>
        <router-outlet></router-outlet>
      </main>
      <footer>
        <p>&copy; 2023 Interview Application</p>
      </footer>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    header {
      background-color: #3f51b5;
      color: white;
      padding: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    nav a {
      color: white;
      text-decoration: none;
      margin-left: 1rem;
    }
    main {
      flex: 1;
      padding: 2rem;
    }
    footer {
      background-color: #f5f5f5;
      padding: 1rem;
      text-align: center;
    }
  `]
})
export class AppComponent {
  constructor(private apiService: ApiService, private router: Router) {}

  get isLoggedIn(): boolean {
    return this.apiService.isLoggedIn();
  }

  logout(): void {
    this.apiService.logout().subscribe(
      () => {
        this.router.navigate(['/login']);
      },
      error => {
        console.error('Logout failed', error);
      }
    );
  }
}