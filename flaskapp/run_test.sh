#!/bin/bash
# Запускаем Flask приложение через Gunicorn
gunicorn --bind 127.0.0.1:5000 wsgi:app &
APP_PID=$!

# Ждём запуска
sleep 5

# Запускаем тесты
python3 client.py
TEST_RESULT=$?

# Останавливаем сервер
kill -TERM $APP_PID
sleep 2

# Возвращаем код результата тестов
exit $TEST_RESULT
