# Flask Backend Pseudo-code

# Import necessary modules
# Flask, session management, etc.

# Initialize Flask app

# Define routes

# Login route
def login():
    # If POST request:
    #   Validate user input (username, password, job_title)
    #   Store username and job_title in session
    #   Return success response
    # If GET request:
    #   Return login page

# Interview route
def interview():
    # If user not logged in:
    #   Redirect to login page
    
    # If POST request (user sent a message):
    #   Get user message from request
    #   Add user message to conversation history
    #   Generate AI response based on job_title and conversation history
    #   Add AI response to conversation history
    #   Return AI response
    
    # If GET request (starting the interview):
    #   Return initial greeting message

# Logout route
def logout():
    # Clear user session
    # Redirect to login page

# Helper functions

def generate_ai_response(job_title, conversation_history):
    # Use conversation history and job_title to generate appropriate response
    # Return AI response

# Run the Flask app