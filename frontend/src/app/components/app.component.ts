import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container">
      <header>
        <h1>Interview Application</h1>
      </header>
      <main>
        <router-outlet></router-outlet>
      </main>
      <footer>
        <p>&copy; 2024 Interview Application</p>
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
      text-align: center;
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
  title = 'Interview Application';
}