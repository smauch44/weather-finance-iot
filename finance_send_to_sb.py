import os, json, requests
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from dotenv import load_dotenv

load_dotenv()

# Load credentials
SERVICE_BUS_CONN_STR = os.getenv("SERVICE_BUS_CONN_STR")
TOPIC_NAME = os.getenv("SERVICE_BUS_TOPIC")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY_ID = 2950159  # Berlin

# Fetch current weather
url = "https://api.openweathermap.org/data/2.5/weather"
params = {"id": CITY_ID, "appid": OPENWEATHER_API_KEY, "units": "metric"}
resp = requests.get(url, params=params, timeout=10)
resp.raise_for_status()
data = resp.json()

msg_body = {
    "city": data["name"],
    "temp": data["main"]["temp"],
    "feels_like": data["main"]["feels_like"],
    "condition": data["weather"][0]["description"],
    "humidity": data["main"]["humidity"],
    "wind": data["wind"]["speed"]
}

# Send to Service Bus topic
with ServiceBusClient.from_connection_string(SERVICE_BUS_CONN_STR) as client:
    sender = client.get_topic_sender(topic_name=TOPIC_NAME)
    with sender:
        message = ServiceBusMessage(json.dumps(msg_body))
        sender.send_messages(message)
        print("✅ Weather message sent to Service Bus.")
