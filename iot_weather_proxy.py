
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
DEVICE_CONN = os.getenv("IOTHUB_DEVICE_CONN_STR_WEATHER")
CITY_ID = 2950159  # Berlin

if not API_KEY or not DEVICE_CONN:
    raise RuntimeError("Missing OPENWEATHER_API_KEY or IOTHUB_DEVICE_CONN_STR_WEATHER")

def main():
    # fetch weather
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"id": CITY_ID, "appid": API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    d = r.json()
    payload = {
        "type": "weather",
        "city": d["name"],
        "city_id": CITY_ID,
        "temperature_c": d["main"]["temp"],
        "feels_like_c": d["main"]["feels_like"],
        "condition": d["weather"][0]["description"],
        "humidity": d["main"]["humidity"],
        "wind_ms": d["wind"]["speed"],
        "source": "openweathermap",
    }
    print("Sending to IoT Hub:", payload)
    client = IoTHubDeviceClient.create_from_connection_string(DEVICE_CONN)
    client.connect()
    client.send_message(Message(json.dumps(payload)))
    client.disconnect()
    print("✅ weather proxy → IoT Hub sent")

if __name__ == "__main__":
    main()
