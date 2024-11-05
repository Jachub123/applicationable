// Angular Frontend Pseudo-code

// Import necessary Angular modules

// API Service
class ApiService {
  // Constructor with HttpClient

  login(username: string, password: string, jobTitle: string) {
    // Send POST request to /login
    // Return observable
  }

  startInterview() {
    // Send GET request to /interview
    // Return observable
  }

  sendMessage(message: string) {
    // Send POST request to /interview with message
    // Return observable
  }

  logout() {
    // Send GET request to /logout
    // Return observable
  }
}

// Login Component
class LoginComponent {
  // Properties for username, password, and jobTitle

  onSubmit() {
    // Call ApiService.login()
    // If successful, navigate to InterviewComponent
    // If error, display error message
  }
}

// Interview Component
class InterviewComponent {
  // Properties for messages array, current message

  ngOnInit() {
    // Call ApiService.startInterview()
    // Add initial message to messages array
  }

  sendMessage() {
    // Call ApiService.sendMessage()
    // Add user message to messages array
    // When response received, add AI message to messages array
  }

  endInterview() {
    // Call ApiService.logout()
    // Navigate to LoginComponent
  }
}

// App Component
class AppComponent {
  // Main app structure
  // Router outlet for displaying LoginComponent or InterviewComponent
}

// App Module
// Define and import all necessary modules and components