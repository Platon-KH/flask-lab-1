import requests
import sys

try:
    # Тестируем главную страницу
    print("Testing main page...")
    r = requests.get('http://localhost:5000/', timeout=10)
    print(f"Status code: {r.status_code}")
    print(f"Response text: {r.text[:100]}...")
    
    # Проверяем содержание
    if r.status_code == 200 and "Hello World" in r.text:
        print("✓ Test passed! Main page works correctly.")
        sys.exit(0)
    else:
        print("✗ Test failed! Main page not working.")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server!")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
