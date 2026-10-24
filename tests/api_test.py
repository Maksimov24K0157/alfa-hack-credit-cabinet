import requests

url = "http://127.0.0.1:8000/test?p=7"

response = requests.get(url).json()

print(response)