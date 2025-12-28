#!/bin/bash

echo "=========================================="
echo "     FLASK APPLICATION TEST SCRIPT"
echo "=========================================="

# Функция для очистки
cleanup() {
    echo "Cleaning up..."
    # Убиваем все процессы gunicorn
    pkill -f gunicorn 2>/dev/null || true
    sleep 2
}

# Регистрируем функцию очистки при выходе
trap cleanup EXIT

echo ""
echo "Step 1: Checking Python and dependencies..."
python --version
pip list | grep -E "(flask|gunicorn|requests|Pillow|numpy|matplotlib)"

echo ""
echo "Step 2: Starting Gunicorn server..."
cd "$(dirname "$0")" || exit 1

# Запускаем сервер в фоне
gunicorn --bind 127.0.0.1:5000 wsgi:app \
    --workers 1 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --daemon

APP_PID=$!
echo "Server started with PID: $APP_PID"

echo ""
echo "Step 3: Waiting for server to be ready..."
for i in {1..15}; do
    sleep 2
    
    # Проверяем, жив ли процесс
    if ! kill -0 $APP_PID 2>/dev/null; then
        echo "✗ Server process died!"
        ps aux | grep gunicorn
        exit 1
    fi
    
    # Пробуем подключиться
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null | grep -q "200"; then
        echo "✓ Server is responding (attempt $i)"
        break
    fi
    
    echo "  Waiting... (attempt $i)"
    
    if [ $i -eq 15 ]; then
        echo "✗ Server failed to start within 30 seconds"
        echo "Current processes:"
        ps aux | grep gunicorn
        echo "Port 5000 status:"
        netstat -tulpn | grep :5000 || true
        exit 1
    fi
done

echo ""
echo "Step 4: Running comprehensive tests..."
python client.py
TEST_RESULT=$?

echo ""
echo "Step 5: Stopping server..."
kill -TERM $APP_PID 2>/dev/null || true
sleep 3

# Проверяем, что процесс убит
if kill -0 $APP_PID 2>/dev/null; then
    echo "Server still running, forcing kill..."
    kill -9 $APP_PID 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "Test completed with exit code: $TEST_RESULT"
echo "=========================================="

exit $TEST_RESULT
