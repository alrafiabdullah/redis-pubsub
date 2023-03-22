release: python manage.py migrate && python manage.py collectstatic --no-input

web: daphne redis_pubsub.asgi:application -b 0.0.0.0 -p $PORT