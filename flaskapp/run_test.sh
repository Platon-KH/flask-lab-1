#!/bin/bash

gunicorn --bind 127.0.0.1:5000 wsgi:app &
APP_PID=$!

sleep 5

python3 client.py
APP_CODE=$?

sleep 2

kill -TERM $APP_PID

exit $APP_CODE
