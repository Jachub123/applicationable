#!/bin/bash

# Build backend
echo "Building backend..."
python build.py

# Build frontend
echo "Building frontend..."
node build_frontend.js

echo "Build process completed."