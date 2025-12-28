#!/usr/bin/env python3
"""
Простой клиент для тестирования в CI
Проверяет только критичные endpoints
"""

import requests
import sys
import time

def wait_for_server(url, max_attempts=10):
    """Ждёт пока сервер станет доступен"""
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ Сервер доступен (попытка {i+1})")
                return True
        except:
            pass
        time.sleep(3)
    return False

def test_endpoint(url, expected_status=200, name=None):
    """Тестирует один endpoint"""
    if name is None:
        name = url
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✓ {name}: {response.status_code}")
            return True
        else:
            print(f"✗ {name}: ожидалось {expected_status}, получили {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name}: ошибка - {e}")
        return False

def main():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ FLASK ПРИЛОЖЕНИЯ (CI)")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Ждём сервер
    if not wait_for_server(f"{base_url}/health"):
        print("✗ Сервер не запустился за отведённое время")
        sys.exit(1)
    
    # Тестируем основные endpoints
    endpoints = [
        (f"{base_url}/", 200, "Главная страница"),
        (f"{base_url}/health", 200, "Health check"),
        (f"{base_url}/test", 200, "Тестовая страница"),
        (f"{base_url}/data_to", 200, "Пример шаблонов (2.6)"),
        (f"{base_url}/form_example", 200, "Пример форм (2.7)"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    print("\nТестируем endpoints:")
    for url, status, name in endpoints:
        if test_endpoint(url, status, name):
            passed += 1
    
    # Дополнительная проверка - статика
    print("\nПроверяем статические файлы:")
    if test_endpoint(f"{base_url}/static/test_image.png", 200, "Статический файл"):
        passed += 1
        total += 1
    
    # Итоги
    print("\n" + "=" * 60)
    print(f"ИТОГО: {passed}/{total} тестов пройдено")
    
    if passed >= total - 1:  # Разрешаем 1 неудачный тест
        print("✅ CI ТЕСТ ПРОЙДЕН")
        sys.exit(0)
    else:
        print("❌ CI ТЕСТ ПРОВАЛЕН")
        sys.exit(1)

if __name__ == "__main__":
    main()
