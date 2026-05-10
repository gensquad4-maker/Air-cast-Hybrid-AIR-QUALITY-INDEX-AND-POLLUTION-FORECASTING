
import requests
import json

WAQI_BASE = "https://api.waqi.info"
TOKEN = "demo"

def test_city(city):
    url = f"{WAQI_BASE}/feed/{city}/?token={TOKEN}"
    resp = requests.get(url)
    print(json.dumps(resp.json(), indent=2))

test_city("Chennai")
