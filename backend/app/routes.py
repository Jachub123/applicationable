from flask import session, redirect, url_for, request, render_template, jsonify
from app import app
from app.model import Interviewer
from app.utils import generate_message, organizer, delete_user_entries, show_user_history

user_histories = {}

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        history = user_histories.get(username, [])
        return render_template('index.html', username=username, history=history)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('user')
        password = data.get('pass')
        text = "hier ist die antwort von chatgpt"
        hist = "dies ist die sammlung der historie"
        phase = "dies ist die phase"
        return jsonify({'response': text, 'historie': hist, 'phase': phase}), 200
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        delete_user_entries(username)
        session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_entry():
    if 'username' in session:
        username = session['username']
        answer = request.form['entry']
        interview_phase = "answer"
        user_histories[username].append({'speaker': 'user', 'interview_phase': interview_phase, 'content': answer})
        response = Panel(username, answer)
        if response:
            user_histories[username].append(response)
    return redirect(url_for('home'))

def Panel(username, user_message):
    import random
    interview_phase = "question"
    anz_loops = 1
    members_list = ['Moderator', 'HR', 'Manager', 'Specialist']
    content_list = ['question', 'evaluation', 'feedback', 'discussion']
    history = user_histories.get(username, [])
    job_position = 'CAE engineering position in structural dynamics with FEM.'
    for interview_phase in content_list:
        available_roles = organizer(members_list, anz_loops, history, interview_phase)
        if available_roles and interview_phase == "question":
            speaker = random.choice(available_roles)
            messages = generate_message(speaker, history, job_position, interview_phase)
            response = Interviewer.speak(speaker, messages)
            content = response.content
            content_dict = json.loads(content)
            statement = content_dict.get('content')
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
        elif available_roles and interview_phase == "evaluation":
            for speaker in members_list:
                messages = generate_message(speaker, history, job_position, interview_phase)
                response = Interviewer.speak(speaker, messages)
                content = response.content
                content_dict = json.loads(content)
                evaluation = content_dict.get('evaluation')
                recommendation = content_dict.get('recommendation')
                user_histories[username].append({'speaker': speaker, 'interview_phase': 'evaluation', 'content': evaluation})
                user_histories[username].append({'speaker': speaker, 'interview_phase': 'recommendation', 'content': recommendation})
            speaker = 'Moderator'
            statement = 'please find the Panels evaluation and recommendation in comments above'
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
        elif len(available_roles) == len(members_list) and interview_phase == "feedback":
            speaker = 'Moderator'
            assessment_history = [d for d in history if d['interview_phase'] in ('evaluation', 'recommendation')]
            messages = generate_message(speaker, assessment_history, job_position, interview_phase)
            response = Interviewer.speak(speaker, messages)
            content = response.content
            content_dict = json.loads(content)
            statement = content_dict.get('content')
            statement = "And here is the overall evaluation and recommendation of the Panel: " + statement
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
        elif available_roles and interview_phase == "discussion":
            speaker = random.choice(available_roles)
            messages = generate_message(speaker, history, job_position, interview_phase)
            response = Interviewer.speak(speaker, messages)
            content = response.content
            content_dict = json.loads(content)
            statement = content_dict.get('content')
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
