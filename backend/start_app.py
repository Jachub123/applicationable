import subprocess
import webbrowser
import time

def start_backend():
    print("Starting the backend...")
    subprocess.Popen(["python", "app.py"])

def open_browser():
    print("Opening the application in your default web browser...")
    webbrowser.open('http://localhost:5000')

if __name__ == "__main__":
    start_backend()
    time.sleep(2)  # Give the backend a moment to start
    open_browser()
    print("Application started. Press Ctrl+C to stop the server when you're done.")