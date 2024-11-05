import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs';
import * as InterviewActions from '../store/interview.actions';
import { InterviewState } from '../store/interview.reducer';

@Component({
  selector: 'app-interview',
  template: `
    <div *ngIf="!(error$ | async)" class="interview-container">
      <h2>Interview for {{ jobTitle }}</h2>
      <div class="messages" #messagesContainer>
        <div *ngFor="let message of (messages$ | async)" [ngClass]="{'ai-message': message.sender === 'AI', 'user-message': message.sender === 'You'}">
          <strong>{{ message.sender }}:</strong> {{ message.content }}
        </div>
      </div>
      <button *ngIf="canLoadMore$ | async" (click)="loadMoreMessages()" [disabled]="loading$ | async">
        Load More Messages
      </button>
      <form (ngSubmit)="sendMessage()" class="message-form">
        <input [(ngModel)]="currentMessage" name="message" placeholder="Your response" required [disabled]="(loading$ | async)">
        <button type="submit" [disabled]="!currentMessage.trim() || (loading$ | async)">{{ (loading$ | async) ? 'Sending...' : 'Send' }}</button>
      </form>
      <button (click)="endInterview()" class="end-interview" [disabled]="(loading$ | async)">End Interview</button>
    </div>
    <div *ngIf="(error$ | async)" class="error">
      <p>{{ error$ | async }}</p>
      <button (click)="startInterview()">Retry</button>
    </div>
  `,
  styles: [`
    .interview-container { max-width: 800px; margin: 0 auto; padding: 20px; }
    .messages { max-height: 400px; overflow-y: auto; margin-bottom: 20px; border: 1px solid #ccc; padding: 10px; }
    .ai-message { background-color: #e6f3ff; padding: 10px; margin: 5px 0; border-radius: 5px; }
    .user-message { background-color: #f0f0f0; padding: 10px; margin: 5px 0; border-radius: 5px; }
    .message-form { display: flex; margin-bottom: 10px; }
    .message-form input { flex-grow: 1; padding: 5px; margin-right: 10px; }
    .message-form button:disabled, .end-interview:disabled { background-color: #cccccc; cursor: not-allowed; }
    .end-interview { background-color: #f44336; color: white; border: none; padding: 10px 20px; cursor: pointer; }
    .error { color: red; text-align: center; }
  `]
})
export class InterviewComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer: ElementRef;

  messages$: Observable<{ sender: string; content: string }[]>;
  loading$: Observable<boolean>;
  error$: Observable<string | null>;
  canLoadMore$: Observable<boolean>;
  currentMessage: string = '';
  jobTitle: string = '';

  constructor(private store: Store<{ interview: InterviewState }>, private router: Router) {
    this.messages$ = this.store.select(state => state.interview.messages);
    this.loading$ = this.store.select(state => state.interview.loading);
    this.error$ = this.store.select(state => state.interview.error);
    this.canLoadMore$ = this.store.select(state => 
      state.interview.totalMessages > state.interview.messages.length
    );
  }

  ngOnInit() {
    this.jobTitle = localStorage.getItem('jobTitle') || 'Unknown Position';
    this.startInterview();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  startInterview() {
    this.store.dispatch(InterviewActions.startInterview({ page: 1, perPage: 10 }));
  }

  sendMessage() {
    if (this.currentMessage.trim()) {
      this.store.dispatch(InterviewActions.sendMessage({ message: this.currentMessage }));
      this.currentMessage = '';
    }
  }

  loadMoreMessages() {
    this.store.select(state => state.interview).subscribe(interviewState => {
      const nextPage = interviewState.currentPage + 1;
      this.store.dispatch(InterviewActions.loadMoreMessages({ page: nextPage, perPage: interviewState.perPage }));
    }).unsubscribe();
  }

  endInterview() {
    this.store.dispatch(InterviewActions.endInterview());
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }
}