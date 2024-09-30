#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment process..."

# Deploy backend
echo "Deploying backend..."
./deploy_backend.sh

# Deploy frontend
echo "Deploying frontend..."
./deploy_frontend.sh

echo "Deployment process completed successfully!"