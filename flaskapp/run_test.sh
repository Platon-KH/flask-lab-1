#!/bin/bash
# Запускаем Flask приложение через Gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind 127.0.0.1:5000 wsgi:app --daemon
APP_PID=$!

# Ждём запуска
echo "Waiting for server to start..."
sleep 5

# Запускаем тесты
echo "Running tests..."
python client.py
TEST_RESULT=$?

# Останавливаем сервер
echo "Stopping server..."
kill -TERM $APP_PID
sleep 2

# Возвращаем код результата тестов
echo "Test result: $TEST_RESULT"
exit $TEST_RESULT
