import { createAction, props } from '@ngrx/store';

export const startInterview = createAction(
  '[Interview] Start Interview',
  props<{ page: number; perPage: number }>()
);
export const startInterviewSuccess = createAction(
  '[Interview] Start Interview Success',
  props<{ messages: any[]; totalMessages: number; currentPage: number; perPage: number }>()
);
export const startInterviewFailure = createAction(
  '[Interview] Start Interview Failure',
  props<{ error: string }>()
);

export const sendMessage = createAction(
  '[Interview] Send Message',
  props<{ message: string }>()
);
export const sendMessageSuccess = createAction(
  '[Interview] Send Message Success',
  props<{ message: string }>()
);
export const sendMessageFailure = createAction(
  '[Interview] Send Message Failure',
  props<{ error: string }>()
);

export const loadMoreMessages = createAction(
  '[Interview] Load More Messages',
  props<{ page: number; perPage: number }>()
);
export const loadMoreMessagesSuccess = createAction(
  '[Interview] Load More Messages Success',
  props<{ messages: any[]; totalMessages: number; currentPage: number; perPage: number }>()
);
export const loadMoreMessagesFailure = createAction(
  '[Interview] Load More Messages Failure',
  props<{ error: string }>()
);

export const endInterview = createAction('[Interview] End Interview');
export const endInterviewSuccess = createAction('[Interview] End Interview Success');
export const endInterviewFailure = createAction(
  '[Interview] End Interview Failure',
  props<{ error: string }>()
);