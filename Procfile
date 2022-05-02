release: python manage.py migrate
web: gunicorn diyblog.wsgi:application --log-file - --log-level debug