import { createReducer, on } from '@ngrx/store';
import * as InterviewActions from './interview.actions';

export interface InterviewState {
  messages: { sender: string; content: string }[];
  loading: boolean;
  error: string | null;
  totalMessages: number;
  currentPage: number;
  perPage: number;
}

export const initialState: InterviewState = {
  messages: [],
  loading: false,
  error: null,
  totalMessages: 0,
  currentPage: 1,
  perPage: 10,
};

export const interviewReducer = createReducer(
  initialState,
  on(InterviewActions.startInterview, (state) => ({ ...state, loading: true })),
  on(InterviewActions.startInterviewSuccess, (state, { messages, totalMessages, currentPage, perPage }) => ({
    ...state,
    loading: false,
    messages,
    totalMessages,
    currentPage,
    perPage,
  })),
  on(InterviewActions.startInterviewFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),
  on(InterviewActions.sendMessage, (state, { message }) => ({
    ...state,
    loading: true,
    messages: [...state.messages, { sender: 'You', content: message }],
  })),
  on(InterviewActions.sendMessageSuccess, (state, { message }) => ({
    ...state,
    loading: false,
    messages: [...state.messages, { sender: 'AI', content: message }],
    totalMessages: state.totalMessages + 2,
  })),
  on(InterviewActions.sendMessageFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),
  on(InterviewActions.loadMoreMessages, (state) => ({ ...state, loading: true })),
  on(InterviewActions.loadMoreMessagesSuccess, (state, { messages, totalMessages, currentPage, perPage }) => ({
    ...state,
    loading: false,
    messages: [...state.messages, ...messages],
    totalMessages,
    currentPage,
    perPage,
  })),
  on(InterviewActions.loadMoreMessagesFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),
  on(InterviewActions.endInterview, (state) => ({ ...state, loading: true })),
  on(InterviewActions.endInterviewSuccess, (state) => ({
    ...initialState,
  })),
  on(InterviewActions.endInterviewFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  }))
);