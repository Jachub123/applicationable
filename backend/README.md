# Interview Application

This is a multi-user interview application with a Flask backend and a JavaScript frontend. The application uses Flask sessions to manage user state and interview progress.

## Prerequisites

Ensure you have Python installed on your system.

## Installation

1. Clone this repository or download the source code.
2. Navigate to the project directory:
   ```
   cd path/to/project
   ```
3. Install the required Python packages:
   ```
   pip install flask flask-cors
   ```

## Starting the Application

We've provided a simple script to start both the backend and frontend:

1. Run the following command:
   ```
   python start_app.py
   ```
2. The script will start the Flask server and open the application in your default web browser.
    In Angular applications, the frontend is started using ng serve. However, in our current setup, 
    we're not using a full Angular application. Instead, we have a simpler JavaScript frontend 
    that's being served directly by our Flask backend. Let me explain how it's working in our case:

    app = Flask(__name__, static_folder='../frontend/src', static_url_path='')


Our frontend is a simple HTML file with JavaScript (main.js) that's not using the full Angular framework.
The Flask backend is configured to serve static files, including our HTML and JavaScript files.
When you run the Flask server (app.py), it serves both the API endpoints and the frontend files.
Here's how it's set up in our app.py:

app = Flask(__name__, static_folder='../frontend/src', static_url_path='')

3. If the browser doesn't open automatically, navigate to `http://localhost:5000`.

Alternatively, you can start the backend manually:

1. Navigate to the backend directory:
   ```
   cd path/to/backend
   ```
2. Start the Flask server:
   ```
   python app.py
   ```
3. Open a web browser and go to `http://localhost:5000`.

## Usage

1. Log in with a username, password, and job title.
2. The application will start an interview session, asking questions based on the provided job title.
3. Answer the questions presented in the interview.
4. The conversation history and current question will be displayed on the screen.
5. When finished, click the "End Interview" button to log out.

## Features

- Multi-user support with separate interview sessions for each user.
- Job-specific questions based on the provided job title.
- Conversation history maintained throughout the interview.
- Efficient communication between frontend and backend using Flask sessions.

## Stopping the Application

To stop the application, press Ctrl+C in the terminal where you started the server.

## Development

- The backend code is in `app.py`.
- The frontend code is in `../frontend/src/main.js`.
- The application uses Flask sessions to manage user state and interview progress.

Note: This is a development setup and should not be used in a production environment without proper security measures.