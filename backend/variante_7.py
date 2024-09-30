# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:26:19 2024

@author: User
"""
###############################################################################

from datetime import timedelta
import requests, json, os
import pprint
from uuid import uuid4

print("current history")
pp = pprint.PrettyPrinter(indent=4)

###############################################################################
from flask import Flask, session, redirect, url_for, request, render_template, make_response
from flask import jsonify
from flask_cors import CORS
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

class CustomSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False

class CustomSessionInterface(SessionInterface):
    def __init__(self):
        self.store = {}

    def open_session(self, app, request):
        sid = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        if sid:
            stored_session = self.store.get(sid)
            if stored_session:
                return CustomSession(initial=stored_session, sid=sid)
        sid = str(uuid4())
        return CustomSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.config['SESSION_COOKIE_NAME'], domain=domain, path=path)
            return
        self.store[session.sid] = dict(session)
        response.set_cookie(app.config['SESSION_COOKIE_NAME'], session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain, path=path, secure=False, samesite='Lax')

if True:
    # Disable access log messages
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)     # disable Default Flask access log messages
    
app = Flask(__name__, template_folder='./templates_1')
app.wsgi_app = ProxyFix(app.wsgi_app)

# Use a fixed secret key
app.secret_key = 'your_fixed_secret_key_here'  # Replace with a strong, random key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'null'
app.config['SESSION_COOKIE_NAME'] = 'custom_session'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.session_interface = CustomSessionInterface()

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5050"}})

@app.before_request
def before_request():
    print(f"Before request: Session contents: {session}")
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No SID'}")
    print(f"Request cookies: {request.cookies}")
    print(f"Request path: {request.path}")
    print(f"Is session modified: {session.modified}")
    print(f"Session permanent: {getattr(session, 'permanent', False)}")

###############################################################################
# define LLM

class Model:
    
    #--------------------------------------------------------------------------
    def __init__(self):

        from openai import OpenAI
        
        print("\n-------------------------------------------------------") 
        print("\n - initialize LLM")
        
        Openai_key  = "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"
        self.client = OpenAI(api_key = Openai_key)
        self.temp   = 1.0
        self.model  = "gpt-4o-mini"
        #self.model  = "gpt-4o"
        #self.seed  = 123

        return
    
    #--------------------------------------------------------------------------
    def speak(self, speaker, task):
                
        print("\n-------------------------------------------------------") 
        print("\n - ", speaker, "says:")
        
        completion = self.client.chat.completions.create(
                      model    = self.model,
                      messages = task,
                      response_format={"type": "json_object"}
                    )
        response = completion.choices[0].message
        
        # print(" - ", response)
        
        return response

Interviewer = Model()

###############################################################################
# In-memory storage for user histories
user_histories = {}

###############################################################################
# user browser has sent a GET request to "/" meaning "give me content of the
# root page. Flask finds @app.route('/') decorator which is assiciated with
# home function
@app.route('/')
def home():
    print("Home route accessed")
    print("Session contents:", session)
    
    # check if session object contains username: 
    if 'username' in session:
        # if username present then user is logged in, then get username and history
        username = session['username']
        history  = user_histories.get(username, [])

        print(f"Session object found, username: {username}")
        
        # flask processes index.html populating it with username and history 
        # and sends it to users browser
        return render_template('index.html', username=username, history=history)
    
    else:
        print("No session object found, redirecting to login")

    # if username is not present redirect to login
    return redirect(url_for('login'))

###############################################################################
# when the user first navigates to /login the browser sends a GET request
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")
    print("Session contents before login:", session)
    
    if request.method == 'POST':
        print("Login POST request received")
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            username = data.get('user')
            password = data.get('pass')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        print("Login attempt - Username:", username)
        
        # Here you should implement proper authentication
        # For demonstration, we'll assume the login is successful if a username is provided
        if username:
            print("Login successful, creating session object")
            try:
                session.clear()
                session['username'] = username
                session['user_id'] = str(uuid4())  # Generate a unique user ID
                session.permanent = True
                session.modified = True
                user_histories[username] = []  # Initialize user history
                print("Session after login:", session)
                response = make_response(redirect(url_for('home')))
                return response
            except Exception as e:
                print(f"Error setting session: {e}")
                return render_template('login.html', error="An error occurred during login")
        else:
            print("Login failed - no username provided")
            return render_template('login.html', error="Invalid credentials")
    
    # If it's a GET request, render the login page
    return render_template('login.html')

###############################################################################
@app.route('/logout')
def logout():
    print("Logout route accessed")
    print("Session before logout:", session)
    # delete user history
    if 'username' in session:
        username = session['username']
        delete_user_entries(username)
        # delete session of user
        session.clear()
    print("Session after logout:", session)
    response = make_response(redirect(url_for('login')))
    response.set_cookie(app.config['SESSION_COOKIE_NAME'], '', expires=0)
    return response

###############################################################################
@app.route('/add', methods=['POST'])
def add_entry():
    if 'username' in session:
        
        username     = session['username']
        answer       = request.form['entry']
        interview_phase = "answer"  
        user_histories[username].append({'speaker':         'user', 
                                         'interview_phase': interview_phase, 
                                         'content':         answer})

        # Get response from LLM
        # Get response from LLM
        response = Panel(username, answer)
        if response:
            user_histories[username].append(response)

    return redirect(url_for('home'))

###############################################################################
@app.route('/debug')
def debug():
    return jsonify({
        'session': dict(session),
        'cookies': dict(request.cookies)
    })

###############################################################################
def Panel(username, user_message):
    
    import random
    #show_user_history(username)
    
    interview_phase = "question"
    
    
    anz_loops     = 1
    members_list  = [ 'Moderator', 'HR', 'Manager', 'Specialist' ]
    content_list  = [ 'question', 'evaluation', 'feedback', 'discussion']     # , 'introduction', 'recommendation'
        
    
    history = user_histories.get(username, [])
    
    # print("hostory");print(history)

    job_position = 'CAE engineering position in structural dynamics with FEM.'
    history = user_histories.get(username, [])
    
    # Interview Steuerung: interaktive loop für Fragerunde (question)
    for interview_phase in content_list:
        available_roles = organizer(members_list, anz_loops, history, interview_phase)
        
        print("interview_phase", interview_phase)
        print("available_roles", available_roles)
        
        #----------------------------------------------------------------------
        # Fragerunde noch nicht abgeschlossen 
        if available_roles and interview_phase == "question": 
            print("\n still more", interview_phase, "to do for", available_roles)
            
            speaker  = random.choice(available_roles)
            messages = generate_message(speaker, history, job_position, interview_phase)
    
            if True: print("\n - randomly selected speaker:", speaker, "out of", available_roles)                    
            
            response = Interviewer.speak(speaker, messages)
            content  = response.content
                
            # Parse the JSON string into a Python dictionary: json_string = '{"speaker": "Moderator", "message": "Hello}'
            content_dict = json.loads(content)
        
            # Extract speaker and message to candidate
            statement = content_dict.get('content')
            
            print(f"Speaker: {speaker}")
            print(f"{interview_phase}: {statement}")
    
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
        
        #----------------------------------------------------------------------
        # Fragerunde abgeschlossen , es erfolgt die interne Beratung: evaluation recommendation
        elif available_roles and interview_phase == "evaluation": 
                        
            print("\n starting", interview_phase, "phase")
            
            for speaker in members_list:
            
                messages = generate_message(speaker, history, job_position, interview_phase)         
                response = Interviewer.speak(speaker, messages)
                content  = response.content
                    
                content_dict   = json.loads(content)
                evaluation     = content_dict.get('evaluation')
                recommendation = content_dict.get('recommendation')
                
                # documentation in user_historie
                user_histories[username].append( {'speaker': speaker, 
                                                  'interview_phase': 'evaluation', 
                                                  'content': evaluation} )
                
                user_histories[username].append( {'speaker': speaker, 
                                                  'interview_phase': 'recommendation', 
                                                  'content': recommendation} )    
                
            # return evaluation and recommendation to candidate with statement
            speaker =  'Moderator'
            statement = 'please find the Panels evaluation and recommendation in comments above'
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}
        
        #----------------------------------------------------------------------
        # Fragerunde abgeschlossen , es erfolgt die interne Beratung: evaluation recommendation
        elif len(available_roles) == len(members_list) and interview_phase == "feedback": 
            
            print("\n starting", interview_phase, "phase")
            
            speaker =  'Moderator'
            assessment_history = [d for d in history if d['interview_phase'] in ('evaluation', 'recommendation')]
            messages = generate_message(speaker, assessment_history, job_position, interview_phase)         
            response = Interviewer.speak(speaker, messages)
            content  = response.content
                    
            content_dict = json.loads(content)
            statement    = content_dict.get('content')
            statement    = "And here is the overall evaluation and recommendation of the Panel: " + statement
                
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}

        #----------------------------------------------------------------------
        # Fragerunde abgeschlossen , es erfolgt die interne Beratung: evaluation recommendation
        elif available_roles  and interview_phase == "discussion": 
            
            print("\n starting", interview_phase, "phase")
            
            speaker  = random.choice(available_roles)
            messages = generate_message(speaker, history, job_position, interview_phase)
    
            if True: print("\n - randomly selected speaker:", speaker, "out of", available_roles)                    
            
            response = Interviewer.speak(speaker, messages)
            content  = response.content
                
            # Parse the JSON string into a Python dictionary: json_string = '{"speaker": "Moderator", "message": "Hello}'
            content_dict = json.loads(content)
        
            # Extract speaker and message to candidate
            statement = content_dict.get('content')
            
            print(f"Speaker: {speaker}")
            print(f"{interview_phase}: {statement}")
    
            return {'speaker': speaker, 'interview_phase': interview_phase, 'content': statement}        
            
            
            
###############################################################################
def generate_message(speaker, history, job_position, interview_phase):
    
    messages = []
    
    system_message = {
        'role': 'system',
        'content': (
            "You are member of a job assessment interview panel. Your role is to collectively assess the candidate's skills for a CAE engineering position specializing in fluid dynamics. "
            "The panel consists of a Moderator, HR, Manager, and Specialist. Each role will ask questions relevant to their expertise. "
        )
    }
    
    if interview_phase == "question":
        
        response_format ={"speaker": "your role", "interview_phase": "question", "content": "your message"}
    
        user_message = {
            'role': 'user',
            'content': (
                "As a very skilled member from the companies {}, you are part of a job assessment panel for the position of a {}. "
                "Your task is to assess the candidate's skills relevant to the company. "
                "After each question, wait for the candidate's answer before proceeding to the next one. "
                "Consider all previous answers in your next question to get a complete impression of the candidate's skills. "
                "This is the interview so far:\n{}\n"
                "Ask questions covering relevant topics for this job position, ensuring that you evaluate the candidate's skills with respect to your own area of responsibility. "
                "For example, HR should evaluate social skills, and the manager should evaluate management skills. "
                "Output just the question and no extra text in JSON format {}."
            ).format(speaker, job_position, history, response_format)
        }
        

    if interview_phase == "evaluation":
        
        response_format ={"speaker": "your role", "evaluation": "your evaluation", "recommendation": "your recommendation and recommendation"}
    
        user_message = {
            'role': 'user',
            'content': (
                "As a very skilled member from the companies {}, you are part of a job assessment panel for the position of a {}. "
                "Your task is to provide your evaluation and recommendations based on the candidate's performance. "
                "Consider all aspects of the candidate's skills and responses during the interview. "
                "This is the interview so far:\n{}\n"
                "Evaluate the candidate's performance on a scale from 1 to 10, where 10 is the best."
                "Provide constructive feedback and recommendations to the candidate on how they can improve their skills. "
                "Output your evaluation and recommendations in JSON format {}."
            ).format(speaker, job_position, history, response_format)
        }
 
    if interview_phase == "feedback":
        
        response_format ={"speaker": "Panel as a whole", "interview_phase": "content", "content": "your summary"}
    
        user_message = {
            'role': 'user',
            'content': (
                "You have received evaluations and recommendations from various skilled members of the company regarding a candidate for the position of a {}. "
                "Each member has provided their assessment and feedback."
                "Your task is to create a concise summary based on these evaluations. "
                "Include the key points from the assessments and provide an overall summary in no more than 3 sentences. "
                "Here are the evaluations and recommendations:\n{}\n"
                "Output the summary in in JSON format {}."
            ).format(job_position, history, response_format)
        }

    if interview_phase == "discussion":
        
        response_format = {"speaker": "your role", "interview_phase": "question", "content": "your message"}    
        
        
        # Filtering dicts with interview_phase 'evaluation' or 'recommendation'
        filtered_dicts = [d for d in history if d['interview_phase'] in ('feedback', 'discussion')]
        # Finding the last entry where speaker == 'user': iterates over filtered_dicts in reverse order 
        # to find the first dictionary where speaker is "user". If no such dictionary is found, it returns None.
        last_user_entry = next((d for d in reversed(filtered_dicts) if d['speaker'] == 'user'), None)
        user_input      = last_user_entry['content'] if last_user_entry else None
        
        print("user_input", user_input)
        
        user_message = {
            'role': 'user',
            'content': (
                "You are a skilled member of the company's {} team. Your role is to discuss the summary and assessment results with the candidate."
                "Respond to the latest user input: '{}'. Use the entire session history to inform your response. "
                "This is the session so far:\n{}\n."
                "Provide thoughtful and constructive repsonse to the user input based on the assessments provided by you and other team members. "
                "Ensure your response is clear and actionable. "
                "Output the summary in in JSON format {}."
            ).format(speaker, user_input, history, response_format)
        }

    messages.append(system_message)
    messages.append(user_message)
    
    #print(messages)

    return messages



###############################################################################    
def parse_llm_response(response_text):
    # Assume the LLM returns responses in the format "Role: message"
    if ':' in response_text:
        role, content = response_text.split(':', 1)
        return role.strip().lower(), content.strip()
    else:
        return 'llm', response_text.strip()

###############################################################################
def organizer(members_list, anz_loops, history, interview_phase):
    
    # Count questions asked by each role
    role_question_count = {role: 0 for role in members_list}
    
    print("before role_question_count: \n", role_question_count)

    for message in history:
        
        if message['speaker'] in members_list \
            and message['interview_phase'] == interview_phase :
                role_question_count[message['speaker']] += 1
    
    print("after role_question_count: \n", role_question_count)
    
     # Filter roles that have remaining questions to ask
    available_roles = [role for role in members_list if role_question_count[role] < anz_loops]
        
    return available_roles           
            
###############################################################################
def show_history():
    import pprint
    print("show_history: current history")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(user_histories)

###############################################################################
def show_user_history(username):
    import pprint
    print("show_user_history: current history for", username)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(user_histories[username])
    
###############################################################################
# Function to delete user entries from the history dictionary
def delete_user_entries(user):
    if user in user_histories:
        del user_histories[user]    
        
###############################################################################


if __name__ == '__main__':
    app.run(debug=True, port=5050)