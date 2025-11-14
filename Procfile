web: gunicorn Etu_student_result.wsgi:application --bind 0.0.0.0:10000 --log-file - --timeout 600
release: python manage.py migrate --noinput
