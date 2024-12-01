###############################################################################
# Die zentrale Datenbank des Python Prozesses ist das User spezifische Session 
# Dictionary. Es enthält:
# - username
# - job_title
# - die gesamte Hitorie des Interviews
# - die Phasen des Interviews
# - die aktuelle Aussage (role: "wer spricht"", message:"sagt was")
#
# Das Session Dictonary steht allen Python-Modulen als globales Dictionary
# zur Verfuegung, kann also von allen Modulen gelesen und beschrieben werden.
#
# wir speichern die session history in einem tuple weil
# A tuple is an ordered, immutable collection of items. It can hold a fixed 
# number of elements, and the order in which they appear is preserved. Once 
# a tuple is created, its elements cannot be changed.
#
# Die Kommunikation mit dem Frontend erfolgt dagegen nur über die Historie und 
# die aktuelle Frage/Aussage, weil das Session Dictonary nicht (so einfach) 
# an das Frontend übergeben werden kann.
#
# app.py (dieses Hauptmodul, main)
# - übernimmt die Kommunikation mit dem Frontend
# - übergibt Session Historie sowie die aktuelle Frage/Botschaft and das Frontend
# - nimmt die Antwort vom Frontend entgegen
# - aktualisiert das Session Dictionary mit den Antworten des Frontend
# - übergibt die Steuerung an AI.panel_moderation, also an die Funktion 
#   "panel_moderation" in AI.py
# - empfängt die Antwort der "panel_moderation" (diese wird in das Session-
#   Dictionary geschrieben) und leitet diese wiederum an das Frontend weiter
#
# Inkonsistenz: in Session speichern wir die Historie in 
#                   - session['history'] 
#               an das frontend übergeben wird diese aber als
#                   - 'conversation_history': session['history']
#
# Offene Frage: welche parameter verwendet / benötigt das frontend bei
#               login und interview?
#               Das backend bietet folgendes an:
#                return jsonify({
#                    'username'              : session['username'],
#                    'job_title'             : session['job_title'],
#                    'conversation_history'  : session['history'],
#                    'message'               : session['current_question'],
#                    'current_question'      : session['current_question']
#                }), 200
#
# Fehler:       im login nimmat das frontend keinen dieser parameter an
#
# ak, 29.11.24
###############################################################################
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import timedelta

import AI

# - Sets up Flask with static file serving
# - Configures session handling with 1-hour lifetime
# - Enables CORS for cross-origin requests

app = Flask(__name__, static_folder='../frontend/src', static_url_path='')
app.secret_key = 'your-secret-key'  # Change this to a secure random key in production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

#----------------------------------------------------------------------------------
# cors
CORS(app, 
     supports_credentials=True,
     resources={r"/api/*": {"origins": ["http://localhost:4200"]}},
     allow_headers=["Content-Type"],
     expose_headers=["Access-Control-Allow-Credentials"])

#----------------------------------------------------------------------------------
# Configure logging for the application
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

#----------------------------------------------------------------------------------
# Suppress werkzeug's HTTP access logs (default logs)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Set to ERROR to suppress access logs, only showing errors and above
# Now only errors will be shown in the console, while application logs are still at INFO level in the file

#----------------------------------------------------------------------------------
# In-memory user storage (replace with a database in production)
users    = {}
AI_model = "llama3.2"
AI_model = "gpt-4o-mini"

#----------------------------------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    ''' Takes username, password, job_title
        Creates new user if not exists, or validates existing user
        Initializes session with user data and first question
        Returns session data
    '''
    #--------------------------------------------------------------------
    # get all request data
    data = request.json
    username  = data.get('username')
    password  = data.get('password')
    job_title = data.get('jobTitle')
        
    # job_title = "CAE engineering position specializing in fluid dynamics"
    
    #--------------------------------------------------------------------
    # check user, password and job_title
    
    if not username or not password or not job_title:
        message = f'Warning: Login attempt with missing fields: {data}'
        app.logger.warning(message); print(message)
        # respond missing fields to frontend
        return jsonify({'error': 'Missing required fields'}), 400
    
    if username not in users:
        users[username] = {
            'password': generate_password_hash(password),
            'job_title': job_title
        }
        message = f'New user created: {username}'
        app.logger.info(message) #; print(message)
        
    elif not check_password_hash(users[username]['password'], password):
        message = f'Warning: Failed login attempt for user: {username}'
        app.logger.warning(message); print(message)
        # respond validation error to frontend
        return jsonify({'error': 'Invalid credentials'}), 401
    
    #--------------------------------------------------------------------
    # update session parameters
    session.permanent           = True  # Use the permanent session lifetime
    session['username']         = username
    session['job_title']        = job_title
    session['interview_phase']  = "introduction"
    session['history']          = []
    
    # get AI response to session history, initial indicaates first contact
    AI.panel_moderation(AI_model, initial=True)

    message = f'Successful login: {username}'
    app.logger.info(message) # ; print(message)

    #--------------------------------------------------------------------
    # response to frontend
    return jsonify({
        'username'              : session['username'],
        'job_title'             : session['job_title'],
        'conversation_history'  : session['history']
    }), 200

#----------------------------------------------------------------------------------
@app.route('/api/interview', methods=['GET', 'POST'])
def interview():
    ''' GET: Returns current session state
        POST: Processes user's message and generates AI response
        Maintains conversation history in session
    '''
    
    #--------------------------------------------------------------------
    if 'username' not in session:
        message = 'error: Unauthorized interview access attempt'
        app.logger.warning(message); print(message)
        return jsonify({'error': 'Not logged in'}), 401
    
    #--------------------------------------------------------------------------
    #  GET request ist nicht erlaubt
    if request.method == 'GET':
        return jsonify({'error': 'method GET now allowd'}), 401

    #-------------------------------------------------------------------------
    #  POST request von angemeldetem user (mit hostory) wird von AI beantwortet  
    elif request.method == 'POST':
        user_message = request.json.get('message')
        message = f'interview received message from user: {session["username"]}'
        app.logger.info(message) #; print(message)
        
        # error empty message
        if not user_message:
            message = f'Empty message received from user: {session["username"]}'
            app.logger.warning(message); print(message)
            return jsonify({'error': 'Missing message'}), 400
        
        # user response in session history anhaengen
        session['history'].append(('User', user_message))
        
        # übergabe an AI.panel, dieses schreibt die Antwort direkt in history
        AI.panel_moderation(AI_model)
        
        # panel response zurück an frontend
        return jsonify({
            'username'              : session['username'],
            'job_title'             : session['job_title'],
            'conversation_history'  : session['history']
        }), 200
        #return jsonify({
        #    'username'              : session['username'],
        #    'job_title'             : session['job_title'],
        #    'conversation_history'  : session['history'],
        #    'message'               : session['current_question'],
        #    'current_question'      : session['current_question']
        #}), 200

#----------------------------------------------------------------------------------
@app.route('/api/logout', methods=['POST'])
def logout():
    ''' Clears user session
    Logs out user
    ''' 
    username = session.pop('username', None)
    session.clear()
    app.logger.info(f'User logged out: {username}')
    return jsonify({'message': 'Logged out successfully'}), 200

#----------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
