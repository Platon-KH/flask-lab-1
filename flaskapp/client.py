# flaskapp/client.py
import requests

try:
    resp = requests.get('http://127.0.0.1:5000/')
    assert resp.status_code == 200
    print("Стартовая страница доступна")
except Exception as e:
    print("Ошибка:", e)
    exit(1)
