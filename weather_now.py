# weather_now.py
import requests, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY_ID = 2950159  # Berlin

def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"id": CITY_ID, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return {
        "source": "openweathermap",
        "city": data["name"],
        "city_id": CITY_ID,
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "condition": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_ms": data["wind"]["speed"]
    }

if __name__ == "__main__":
    print(get_weather())
