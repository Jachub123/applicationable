# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:26:19 2024

@author: User
"""
###############################################################################

from datetime import timedelta
import requests, json, os
import pprint

print("current history")
pp = pprint.PrettyPrinter(indent=4)

###############################################################################
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='./templates_1')
CORS(app)

###############################################################################
# In-memory storage for user histories
user_histories = {}

###############################################################################
@app.route('/')
def home():
    # This route will be handled by Angular. We'll just return a success message.
    return jsonify({"message": "Welcome to the home page"}), 200

###############################################################################
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Login attempt:", data)
    
    username = data.get('user')
    password = data.get('pass')
    
    # Here you would typically check the username and password against a database
    # For this example, we'll just check if the username is not empty
    if username:
        # Initialize user history if it doesn't exist
        if username not in user_histories:
            user_histories[username] = []
        
        print(f"User {username} logged in successfully")
        return jsonify({
            'success': True,
            'message': 'Login successful'
        })
    else:
        print("Login failed: Invalid username or password")
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

###############################################################################
@app.route('/user_data', methods=['GET'])
def get_user_data():
    # In a real application, you would validate the session here
    # For now, we'll just check if a username is provided in the query parameters
    username = request.args.get('username')
    if username and username in user_histories:
        return jsonify({
            'username': username,
            'history': user_histories[username]
        })
    else:
        return jsonify({
            'error': 'User not found or not logged in'
        }), 404

###############################################################################
@app.route('/add', methods=['POST'])
def add_entry():
    data = request.get_json()
    username = data.get('username')
    entry = data.get('entry')
    
    if username and entry and username in user_histories:
        user_histories[username].append({
            'speaker': 'user',
            'interview_phase': 'answer',
            'content': entry
        })
        
        # Here you would typically generate a response using your Panel function
        # For this example, we'll just echo the entry
        response = {
            'speaker': 'AI',
            'interview_phase': 'question',
            'content': f"You said: {entry}"
        }
        user_histories[username].append(response)
        
        return jsonify({
            'success': True,
            'message': 'Entry added successfully',
            'response': response
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to add entry'
        }), 400

###############################################################################
# Function to delete user entries from the history dictionary
def delete_user_entries(user):
    if user in user_histories:
        del user_histories[user]    
        
###############################################################################

if __name__ == '__main__':
    app.run(debug=True, port=5050)