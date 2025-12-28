import requests

r1 = requests.get('http://127.0.0.1:5000/')
assert r1.status_code == 200

r2 = requests.get('http://127.0.0.1:5000/data_to')
assert r2.status_code == 200

print("OK")
