
import requests
import json

WAQI_BASE = "https://api.waqi.info"
TOKEN = "demo"

def fetch_realtime_data(city_name, token):
    headers = {"Accept": "application/json"}
    try:
        url = f"{WAQI_BASE}/feed/{city_name}/?token={token}"
        resp = requests.get(url, timeout=12, headers=headers)
        data = resp.json()
        if data.get("status") == "ok":
            return data["data"]
    except Exception as e:
        return str(e)
    return None

cities = ["Chennai", "Delhi", "Mumbai"]
for city in cities:
    data = fetch_realtime_data(city, TOKEN)
    if data:
        print(f"{city}: AQI = {data.get('aqi')}")
    else:
        print(f"{city}: Failed to fetch")
