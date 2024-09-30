#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Deploying Flask backend..."

# Navigate to the backend directory
cd "$(dirname "$0")"

# Activate virtual environment (uncomment and modify if using a virtual environment)
# source venv/bin/activate

# Install or upgrade dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
# flask db upgrade

# Collect static files (if applicable)
# flask static-files collect

# Restart the application server (modify as per your server setup)
# For example, if using Gunicorn:
# sudo systemctl restart myapp

echo "Backend deployment completed successfully!"