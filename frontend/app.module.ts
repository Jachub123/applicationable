import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';

import { AppComponent } from './app.component';
import { LoginComponent } from './login.component';
import { InterviewComponent } from './interview.component';
import { ApiService } from './api.service';
import { AuthGuard } from './auth.guard';
import { interviewReducer } from './interview.reducer';
import { InterviewEffects } from './interview.effects';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'interview', component: InterviewComponent },
];

@NgModule({
  declarations: [AppComponent, LoginComponent, InterviewComponent],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    StoreModule.forRoot({ interview: interviewReducer }),
    EffectsModule.forRoot([InterviewEffects]),
  ],
  providers: [ApiService, AuthGuard],
  bootstrap: [AppComponent],
})
export class AppModule {}
