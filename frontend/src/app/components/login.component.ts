import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-login',
  template: `
    <div class="login-container">
      <h2>Login</h2>
      <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="login-form">
        <div class="form-group">
          <input formControlName="username" placeholder="Username" required>
          <div *ngIf="f.username.touched && f.username.invalid" class="error-message">
            <div *ngIf="f.username.errors?.required">Username is required</div>
          </div>
        </div>
        <div class="form-group">
          <input formControlName="password" type="password" placeholder="Password" required>
          <div *ngIf="f.password.touched && f.password.invalid" class="error-message">
            <div *ngIf="f.password.errors?.required">Password is required</div>
            <div *ngIf="f.password.errors?.minlength">Password must be at least 6 characters</div>
          </div>
        </div>
        <div class="form-group">
          <input formControlName="jobTitle" placeholder="Job Title" required>
          <div *ngIf="f.jobTitle.touched && f.jobTitle.invalid" class="error-message">
            <div *ngIf="f.jobTitle.errors?.required">Job Title is required</div>
          </div>
        </div>
        <button type="submit" [disabled]="loginForm.invalid || isLoading">
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  `,
  styles: [`
    .login-container { max-width: 300px; margin: 0 auto; padding: 20px; }
    .login-form { display: flex; flex-direction: column; }
    .form-group { margin-bottom: 15px; }
    .form-group input { width: 100%; padding: 8px; box-sizing: border-box; }
    .error-message { color: red; font-size: 12px; margin-top: 5px; }
    button { background-color: #4CAF50; color: white; border: none; padding: 10px; cursor: pointer; }
    button:disabled { background-color: #cccccc; cursor: not-allowed; }
    .error { color: red; text-align: center; }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private formBuilder: FormBuilder,
    private router: Router,
    private apiService: ApiService
  ) {
    this.loginForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]],
      jobTitle: ['', Validators.required]
    });
  }

  get f() { return this.loginForm.controls; }

  onSubmit() {
    if (this.loginForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.apiService.login(
      this.f.username.value,
      this.f.password.value,
      this.f.jobTitle.value
    ).subscribe(
      response => {
        console.log('Login successful', response);
        this.router.navigate(['/interview']);
      },
      error => {
        console.error('Login failed', error);
        this.errorMessage = error;
        this.isLoading = false;
      },
      () => {
        this.isLoading = false;
      }
    );
  }
}