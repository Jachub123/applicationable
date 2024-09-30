from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import random
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import timedelta

app = Flask(__name__, static_folder='../frontend/src', static_url_path='')
app.secret_key = 'your-secret-key'  # Change this to a secure random key in production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
CORS(app, supports_credentials=True)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Interview application startup')

# In-memory user storage (replace with a database in production)
users = {}

# Question bank (as before)
question_bank = {
    'general': [
        "Can you tell me about your background and experience?",
        "What are your strengths and weaknesses?",
        "Where do you see yourself in 5 years?",
        "Why do you want to work for our company?",
        "How do you handle stress and pressure?",
    ],
    'technical': {
        'software_developer': [
            "What programming languages are you proficient in?",
            "Can you explain the difference between object-oriented and functional programming?",
            "How do you approach debugging a complex issue?",
            "What's your experience with version control systems?",
            "How do you stay updated with the latest technology trends?",
        ],
        'data_scientist': [
            "Can you explain the difference between supervised and unsupervised learning?",
            "What's your experience with big data technologies?",
            "How do you approach feature selection in a machine learning project?",
            "Can you explain the concept of overfitting and how to prevent it?",
            "What's your experience with deep learning frameworks?",
        ],
        'network_engineer': [
            "Can you explain the OSI model and its layers?",
            "What's your experience with network security protocols?",
            "How do you troubleshoot network connectivity issues?",
            "Can you explain the difference between TCP and UDP?",
            "What's your experience with cloud networking?",
        ],
    },
    'behavioral': [
        "Can you describe a challenging project you worked on and how you overcame obstacles?",
        "How do you handle conflicts in a team environment?",
        "Tell me about a time when you had to meet a tight deadline.",
        "How do you prioritize tasks when working on multiple projects?",
        "Describe a situation where you had to learn a new skill quickly.",
    ]
}

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    job_title = data.get('jobTitle')
    
    if not username or not password or not job_title:
        app.logger.warning(f'Login attempt with missing fields: {data}')
        return jsonify({'error': 'Missing required fields'}), 400
    
    if username not in users:
        users[username] = {
            'password': generate_password_hash(password),
            'job_title': job_title
        }
        app.logger.info(f'New user created: {username}')
    elif not check_password_hash(users[username]['password'], password):
        app.logger.warning(f'Failed login attempt for user: {username}')
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['username'] = username
    session['job_title'] = job_title
    session['conversation_history'] = []
    session['current_question'] = generate_ai_response(job_title, [], initial=True)
    
    app.logger.info(f'Successful login: {username}')
    return jsonify(dict(session)), 200

@app.route('/api/interview', methods=['GET', 'POST'])
def interview():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if request.method == 'GET':
        return jsonify(dict(session)), 200
    
    elif request.method == 'POST':
        user_message = request.json.get('message')
        if not user_message:
            app.logger.warning(f'Empty message received from user: {session["username"]}')
            return jsonify({'error': 'Missing message'}), 400
        
        session['conversation_history'].append(('User', user_message))
        ai_response = generate_ai_response(session['job_title'], session['conversation_history'])
        session['conversation_history'].append(('AI', ai_response))
        session['current_question'] = ai_response
        session.modified = True
        
        app.logger.info(f'Message processed for user: {session["username"]}')
        return jsonify(dict(session)), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    username = session.pop('username', None)
    session.clear()
    app.logger.info(f'User logged out: {username}')
    return jsonify({'message': 'Logged out successfully'}), 200

def generate_ai_response(job_title, history, initial=False):
    if initial:
        return random.choice(question_bank['general'])
    
    # Determine the appropriate technical questions based on job title
    technical_questions = question_bank['technical'].get(job_title.lower().replace(' ', '_'), [])
    if not technical_questions:
        technical_questions = random.choice(list(question_bank['technical'].values()))

    if len(history) < 3:
        return random.choice(question_bank['general'] + technical_questions)
    elif len(history) < 6:
        return random.choice(technical_questions + question_bank['behavioral'])
    elif len(history) < 9:
        return random.choice(question_bank['behavioral'])
    else:
        return "Thank you for your responses. We've completed the initial interview questions. Is there anything you'd like to ask about the position or the company?"

if __name__ == '__main__':
    app.run(debug=True)