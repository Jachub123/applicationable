import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { of } from 'rxjs';
import { catchError, map, mergeMap, tap } from 'rxjs/operators';
import { ApiService } from '../services/api.service';
import * as InterviewActions from './interview.actions';
import { Router } from '@angular/router';

@Injectable()
export class InterviewEffects {
  startInterview$ = createEffect(() =>
    this.actions$.pipe(
      ofType(InterviewActions.startInterview),
      mergeMap(({ page, perPage }) =>
        this.apiService.startInterview(page, perPage).pipe(
          map((response) => InterviewActions.startInterviewSuccess({
            messages: response.messages,
            totalMessages: response.total_messages,
            currentPage: response.current_page,
            perPage: response.per_page
          })),
          catchError((error) => of(InterviewActions.startInterviewFailure({ error: error.message })))
        )
      )
    )
  );

  sendMessage$ = createEffect(() =>
    this.actions$.pipe(
      ofType(InterviewActions.sendMessage),
      mergeMap((action) =>
        this.apiService.sendMessage(action.message).pipe(
          map((response) => InterviewActions.sendMessageSuccess({ message: response.message })),
          catchError((error) => of(InterviewActions.sendMessageFailure({ error: error.message })))
        )
      )
    )
  );

  loadMoreMessages$ = createEffect(() =>
    this.actions$.pipe(
      ofType(InterviewActions.loadMoreMessages),
      mergeMap(({ page, perPage }) =>
        this.apiService.startInterview(page, perPage).pipe(
          map((response) => InterviewActions.loadMoreMessagesSuccess({
            messages: response.messages,
            totalMessages: response.total_messages,
            currentPage: response.current_page,
            perPage: response.per_page
          })),
          catchError((error) => of(InterviewActions.loadMoreMessagesFailure({ error: error.message })))
        )
      )
    )
  );

  endInterview$ = createEffect(() =>
    this.actions$.pipe(
      ofType(InterviewActions.endInterview),
      mergeMap(() =>
        this.apiService.logout().pipe(
          map(() => InterviewActions.endInterviewSuccess()),
          catchError((error) => of(InterviewActions.endInterviewFailure({ error: error.message })))
        )
      )
    )
  );

  navigateAfterEndInterview$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(InterviewActions.endInterviewSuccess),
        tap(() => this.router.navigate(['/login']))
      ),
    { dispatch: false }
  );

  constructor(
    private actions$: Actions,
    private apiService: ApiService,
    private router: Router
  ) {}
}