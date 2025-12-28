import requests
import sys
import time

def test_main_page():
    """Тест главной страницы"""
    print("Testing main page...")
    try:
        r = requests.get('http://localhost:5000/', timeout=10)
        if r.status_code == 200 and "Обработка изображений" in r.text:
            print("✓ Main page works correctly.")
            return True
        else:
            print(f"✗ Main page failed. Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing main page: {e}")
        return False

def test_data_to_page():
    """Тест страницы /data_to"""
    print("Testing /data_to page...")
    try:
        r = requests.get('http://localhost:5000/data_to', timeout=10)
        if r.status_code == 200:
            print("✓ /data_to page works correctly.")
            return True
        else:
            print(f"✗ /data_to page failed. Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing /data_to page: {e}")
        return False

def test_process_page():
    """Тест страницы /process"""
    print("Testing /process page (GET)...")
    try:
        r = requests.get('http://localhost:5000/process', timeout=10)
        if r.status_code == 200:
            print("✓ /process page works correctly.")
            return True
        else:
            print(f"✗ /process page failed. Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing /process page: {e}")
        return False

def main():
    print("Starting comprehensive tests...")
    
    # Ждём немного чтобы сервер точно запустился
    time.sleep(3)
    
    tests_passed = 0
    total_tests = 3
    
    if test_main_page():
        tests_passed += 1
    
    if test_data_to_page():
        tests_passed += 1
    
    if test_process_page():
        tests_passed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
