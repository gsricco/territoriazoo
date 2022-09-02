#!/bin/bash

#until cd /app/server
#do
#  echo "Waiting for server volume..."
#done

python manage.py migrate

  echo "Waiting for db to be ready..."
  sleep 2


./manage.py collectstatic --noinput

#gunicorn server.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4