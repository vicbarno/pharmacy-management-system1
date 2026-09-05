#!/bin/bash

# Build script for Render.com deployment

# Exit on error
set -e

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Build complete!"
