#!/bin/bash

# Azure App Service startup script for Django

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn digital_signage_project.wsgi:application --bind=0.0.0.0:8000 --workers=2 --threads=4 --timeout=120
