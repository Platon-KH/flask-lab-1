#!/bin/bash

echo "🚀 Запуск тестов в CI окружении"
echo "Текущая директория: $(pwd)"

# Проверяем наличие Python
python3 --version || { echo "❌ Python не найден"; exit 1; }

# Создаём тестовое изображение если его нет
mkdir -p static
if [ ! -f "static/test_image.png" ]; then
    echo "📸 Создаём тестовое изображение..."
    python3 -c "
from PIL import Image
img = Image.new('RGB', (100, 100), color='blue')
for i in range(25, 75):
    for j in range(25, 75):
        img.putpixel((i, j), (255, 0, 0))
img.save('static/test_image.png')
print('Тестовое изображение создано')
" || echo "⚠ Не удалось создать тестовое изображение"
fi

# Запускаем сервер в фоне
echo "🌐 Запускаем Flask сервер..."
cd /home/runner/work/flask-lab-1/flask-lab-1/flaskapp || cd flaskapp
gunicorn --bind 127.0.0.1:5000 wsgi:app \
    --workers 1 \
    --timeout 30 \
    --access-logfile /tmp/gunicorn.log \
    --error-logfile /tmp/gunicorn-error.log \
    --daemon

SERVER_PID=$!
echo "Сервер запущен с PID: $SERVER_PID"

# Ждём запуска
echo "⏳ Ждём запуска сервера (10 секунд)..."
sleep 10

# Проверяем, что процесс жив
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Процесс сервера умер!"
    echo "Логи Gunicorn:"
    cat /tmp/gunicorn-error.log 2>/dev/null || echo "Логи недоступны"
    exit 1
fi

# Запускаем тесты
echo "🧪 Запускаем тесты..."
python3 client.py
TEST_RESULT=$?

# Останавливаем сервер
echo "🛑 Останавливаем сервер..."
kill -TERM $SERVER_PID 2>/dev/null || true
sleep 3

# Проверяем завершение
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "⚠ Сервер не остановился, принудительно завершаем..."
    kill -9 $SERVER_PID 2>/dev/null || true
fi

echo "📊 Результат тестов: $TEST_RESULT"
exit $TEST_RESULT
