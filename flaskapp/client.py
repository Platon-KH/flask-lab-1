import requests

r = requests.get('http://localhost:5000/')
print(f"Status code: {r.status_code}")
print(f"Response text: {r.text[:100]}...")

r2 = requests.get('http://localhost:5000/data_to')
print(f"Status code for /data_to: {r2.status_code}")

if r.status_code == 200 and "Hello World" in r.text:
    print("✓ Test passed!")
    exit(0)
else:
    print("✗ Test failed!")
    exit(1)
