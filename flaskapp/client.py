import requests
import sys
import time

def test_endpoint(url, name, expected_text=None):
    """Тестирует один endpoint"""
    try:
        print(f"Testing {name} ({url})...")
        response = requests.get(url, timeout=15)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            if expected_text and expected_text in response.text:
                print(f"  ✓ {name} works with correct content!")
                return True
            elif not expected_text:
                print(f"  ✓ {name} works!")
                return True
            else:
                print(f"  ✗ {name} works but content mismatch")
                return False
        else:
            print(f"  ✗ {name} failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Cannot connect to {name}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout connecting to {name}")
        return False
    except Exception as e:
        print(f"  ✗ Error testing {name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Starting Flask Application Tests")
    print("=" * 60)
    
    # Даём серверу время запуститься
    print("\nWaiting for server to start...")
    time.sleep(8)
    
    # Тестируемые endpoints
    tests = [
        ("http://localhost:5000/", "Main page", "Обработка изображений"),
        ("http://localhost:5000/test", "Test page", "Test page working"),
        ("http://localhost:5000/health", "Health check", "OK"),
        ("http://localhost:5000/data_to", "Data page", "Пример работы"),
        ("http://localhost:5000/process", "Process page (GET)", "Выберите изображение"),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, name, expected in tests:
        if test_endpoint(url, name, expected):
            passed += 1
        print()
    
    # Дополнительный тест POST запроса
    print("Testing POST to /process...")
    try:
        response = requests.post('http://localhost:5000/process', 
                                data={'shift': '10', 'layers': '5'}, 
                                timeout=10)
        print(f"  POST Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ POST request works!")
            passed += 0.5  # Половина балла
        else:
            print("  ✗ POST request failed")
    except Exception as e:
        print(f"  ✗ POST error: {e}")
    
    total += 0.5  # Добавляем POST тест
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed:.1f}/{total:.1f} tests passed")
    print("=" * 60)
    
    # Требуем минимум 80% успешных тестов
    success_rate = passed / total
    if success_rate >= 0.8:
        print(f"✓ SUCCESS! Success rate: {success_rate:.1%}")
        sys.exit(0)
    else:
        print(f"✗ FAILURE! Success rate: {success_rate:.1%}")
        sys.exit(1)

if __name__ == "__main__":
    main()
