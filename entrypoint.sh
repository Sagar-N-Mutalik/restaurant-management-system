#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Seeding the database with menu and tables..."
# Adding '|| true' ensures that if the seed data already exists 
# and throws an error, it won't crash the server startup.
python manage.py seed_menu || true
python manage.py seed_tables || true

echo "Starting Gunicorn server..."
exec gunicorn core_config.wsgi:application --bind "0.0.0.0:8000"