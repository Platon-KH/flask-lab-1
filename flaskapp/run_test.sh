#!/bin/bash
# flaskapp/run_test.sh

gunicorn --bind 127.0.0.1:5000 wsgi:app &
APP_PID=$!

sleep 5

echo "Запуск клиентского теста..."
python3 client.py
APP_CODE=$?

sleep 2

echo "Остановка Gunicorn (PID: $APP_PID)..."
kill -TERM $APP_PID

exit $APP_CODE
