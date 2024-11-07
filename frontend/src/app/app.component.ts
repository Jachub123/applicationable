import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';
import { LocalStorageService } from './services/local-storage-service.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
  chatData: any = null;
  currentQuestion: string | null = null;
  showChat: boolean = false;
  
  pass: string = '';
  name: string = '';
  job: string = '';
  
  constructor(
    private apiService: ApiService,
    private lss: LocalStorageService
  ) {
    this.loadStoredData();
  }

  ngOnInit(): void {
    console.log('Logged in status:', this.showChat);
  }

  private loadStoredData() {
    const storedChat = this.lss.getItem('chat');
    if (storedChat) {
      this.chatData = JSON.parse(storedChat);
      this.currentQuestion = this.lss.getItem('currentQuestion');
      this.showChat = this.lss.getItem('loggedIn') === 'true';
    }
  }

  register(username: string, password: string, job: string) {
    this.apiService.login(username, password, job).subscribe((data) => {
      this.chatData = data;
      this.currentQuestion = data.current_question;
      this.showChat = true;
      
      this.lss.setItem('chat', JSON.stringify(data));
      this.lss.setItem('currentQuestion', data.current_question);
      this.lss.setItem('loggedIn', 'true');
      
      console.log('Login response:', data);
    });
  }

  logout() {
    this.apiService.logout().subscribe(() => {
      this.chatData = null;
      this.currentQuestion = null;
      this.showChat = false;
      this.lss.clear();
    });
  }

  sendMsg(msg: string) {
    if (!msg.trim()) return;
    
    this.apiService.sendMessage(msg).subscribe((data) => {
      this.chatData = data;
      this.currentQuestion = data.current_question;
      
      this.lss.setItem('chat', JSON.stringify(data));
      this.lss.setItem('currentQuestion', data.current_question);
      
      console.log('Message response:', data);
    });
  }

  getMessageDisplay(historyItem: [string, string]): string {
    const [role, message] = historyItem;
    return `${role}: ${message}`;
  }
}
