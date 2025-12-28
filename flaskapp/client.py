# flaskapp/client.py
import requests

try:
    r = requests.get('http://127.0.0.1:5000/')
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("✅ Главная страница доступна")

    r2 = requests.get('http://127.0.0.1:5000/net')
    assert r2.status_code == 200, f"Expected 200 for /net, got {r2.status_code}"
    print("✅ Страница /net доступна")

except Exception as e:
    print("❌ Ошибка:", e)
    exit(1)
