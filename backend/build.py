import os
import shutil

def build_backend():
    # Create a 'dist' directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')

    # Copy the main application file
    shutil.copy2('app.py', 'dist/app.py')

    # Copy other necessary files (add more as needed)
    necessary_files = ['requirements.txt']
    for file in necessary_files:
        if os.path.exists(file):
            shutil.copy2(file, f'dist/{file}')

    print("Backend build completed. Files are in the 'dist' directory.")

if __name__ == '__main__':
    build_backend()