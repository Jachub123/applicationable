// Simulated Angular app
document.addEventListener('DOMContentLoaded', (event) => {
    const app = document.getElementById('app');
    app.innerHTML = `
        <h2>Interview Application</h2>
        <div id="login-form">
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Password">
            <input type="text" id="jobTitle" placeholder="Job Title">
            <button onclick="login()">Login</button>
        </div>
        <div id="interview-section" style="display: none;">
            <div id="messages"></div>
            <div id="current-question"></div>
            <input type="text" id="user-message" placeholder="Your response">
            <button onclick="sendMessage()">Send</button>
            <button onclick="logout()">End Interview</button>
        </div>
    `;
});

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const jobTitle = document.getElementById('jobTitle').value;

    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, jobTitle }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.username) {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('interview-section').style.display = 'block';
            updateInterview(data);
        } else {
            alert('Login failed: ' + data.error);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function updateInterview(sessionData) {
    const messagesDiv = document.getElementById('messages');
    const currentQuestionDiv = document.getElementById('current-question');
    
    // Display conversation history
    messagesDiv.innerHTML = sessionData.conversation_history.map(msg => 
        `<p><strong>${msg[0]}:</strong> ${msg[1]}</p>`
    ).join('');
    
    // Display current question
    currentQuestionDiv.innerHTML = `<p><strong>AI:</strong> ${sessionData.current_question}</p>`;
}

function sendMessage() {
    const userMessage = document.getElementById('user-message').value;
    const messagesDiv = document.getElementById('messages');
    
    messagesDiv.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;

    fetch('/api/interview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        updateInterview(data);
        document.getElementById('user-message').value = '';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function logout() {
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('interview-section').style.display = 'none';
        document.getElementById('messages').innerHTML = '';
        document.getElementById('current-question').innerHTML = '';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}