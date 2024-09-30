import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SessionService {
  private sessionKey = 'user_session';

  constructor() { }

  setSession(username: string): void {
    localStorage.setItem(this.sessionKey, JSON.stringify({ username, timestamp: new Date().getTime() }));
  }

  getSession(): any {
    const sessionData = localStorage.getItem(this.sessionKey);
    return sessionData ? JSON.parse(sessionData) : null;
  }

  clearSession(): void {
    localStorage.removeItem(this.sessionKey);
  }

  isLoggedIn(): boolean {
    const session = this.getSession();
    if (!session) return false;
    
    // Check if the session is not older than 30 minutes
    const now = new Date().getTime();
    const thirtyMinutes = 30 * 60 * 1000;
    return (now - session.timestamp) < thirtyMinutes;
  }
}