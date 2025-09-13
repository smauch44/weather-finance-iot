# weather_send_to_sb.py
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv
from azure.servicebus import ServiceBusClient, ServiceBusMessage

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
SB_CONN = os.getenv("SERVICE_BUS_CONN_STR")
SB_TOPIC = os.getenv("SERVICE_BUS_TOPIC", "dk-weather-stock-reports")
CITY_ID = 2950159  # Berlin

if not API_KEY:
    raise RuntimeError("Missing OPENWEATHER_API_KEY in .env")
if not SB_CONN:
    raise RuntimeError("Missing SERVICE_BUS_CONN_STR in .env")

# Fetch weather
url = "https://api.openweathermap.org/data/2.5/weather"
params = {"id": CITY_ID, "appid": API_KEY, "units": "metric"}
r = requests.get(url, params=params, timeout=10)
r.raise_for_status()
w = r.json()

payload = {
    "source": "openweathermap",
    "city": w.get("name", "Berlin"),
    "city_id": CITY_ID,
    "temperature_c": w["main"]["temp"],
    "feels_like_c": w["main"]["feels_like"],
    "condition": w["weather"][0]["description"],
    "humidity": w["main"]["humidity"],
    "wind_ms": w["wind"]["speed"],
}

print(f"Sending to topic '{SB_TOPIC}': {payload}")

with ServiceBusClient.from_connection_string(SB_CONN) as sb:
    sender = sb.get_topic_sender(topic_name=SB_TOPIC)
    with sender:
        sender.send_messages(ServiceBusMessage(json.dumps(payload)))
print("✅ weather message sent")

