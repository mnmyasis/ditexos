#!/bin/bash

cd ditexos
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
python manage.py create_first_user
python manage.py create_views

exec gunicorn ditexos.wsgi:application -b 0.0.0.0:8000 --reload