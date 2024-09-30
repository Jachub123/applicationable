#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Deploying Angular frontend..."

# Navigate to the frontend directory
cd "$(dirname "$0")"

# Install dependencies
npm install

# Build the application for production
ng build --configuration production

# Deploy to a web server (modify as per your server setup)
# For example, if deploying to a directory served by Apache or Nginx:
# rsync -avz --delete dist/interview-app/ /var/www/html/interview-app/

echo "Frontend deployment completed successfully!"